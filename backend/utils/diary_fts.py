"""
日记全文检索工具 - 基于 SQLite FTS5
- 创建和管理 FTS5 虚拟表
- 提供全文搜索、BM25 相关性排序、高亮摘要
"""
import sqlite3
import re
import unicodedata

from models.database import DB_PATH


def _get_fts_conn():
    """获取用于 FTS 操作的直接连接（绕过 SQLAlchemy）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_fts5_table():
    """
    初始化 FTS5 虚拟表 travel_diaries_fts
    字段: title, content_plain, city_text, tag_text
    使用 unicode61 tokenizer + tokenchars 支持中文
    """
    conn = _get_fts_conn()
    try:
        # 检查是否已存在
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='travel_diaries_fts'"
        )
        if cursor.fetchone():
            return  # 已存在，跳过

        # 使用最兼容的 unicode61 tokenizer。此前远程分支合并引入的
        # tokenchars 写法在部分 SQLite/FTS5 版本上会直接 parse error。
        try:
            conn.execute("""
                CREATE VIRTUAL TABLE travel_diaries_fts USING fts5(
                    title,
                    content_plain,
                    city_text,
                    tag_text,
                    tokenize='unicode61'
                )
            """)
            conn.commit()
            print("[FTS5] 虚拟表 travel_diaries_fts 创建成功")
        except sqlite3.OperationalError as e:
            conn.rollback()
            print(f"[FTS5] unicode61 tokenizer 初始化失败，降级到默认 tokenizer: {e}")
            conn.execute("""
                CREATE VIRTUAL TABLE travel_diaries_fts USING fts5(
                    title,
                    content_plain,
                    city_text,
                    tag_text
                )
            """)
            conn.commit()
            print("[FTS5] 虚拟表 travel_diaries_fts 已使用默认 tokenizer 创建")
    except Exception as e:
        print(f"[FTS5] 创建虚拟表失败: {e}")
        conn.rollback()
    finally:
        conn.close()


def normalize_title(title: str) -> str:
    """
    标准化标题：统一空格、大小写、全半角
    用于精确查询
    """
    if not title:
        return ""

    # NFKC 规范化（全角转半角等）
    normalized = unicodedata.normalize('NFKC', title)
    # 去除前后空白
    normalized = normalized.strip()
    # 多个连续空格合并为一个
    normalized = re.sub(r'\s+', ' ', normalized)
    # 转小写（英文标题有用，中文无影响）
    normalized = normalized.lower()

    return normalized


def compute_title_hash(title: str) -> str:
    """计算标题的 SHA256 哈希（基于标准化后的标题）"""
    import hashlib
    normalized = normalize_title(title)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def extract_plain_text(content: str, itinerary: list = None) -> str:
    """
    从内容中提取纯文本（去掉HTML标签、JSON结构等）
    用于 FTS 索引
    """
    if not content:
        return ""

    # 简单清理：去掉多余空白行
    text = re.sub(r'\n\s*\n', '\n', content)
    return text.strip()


def extract_city_text(cities: list) -> str:
    """从城市列表提取搜索文本"""
    if not cities:
        return ""
    return " ".join(cities)


def extract_tag_text(diary_type: str = "", companion: str = "", budget: str = "") -> str:
    """从日记元数据提取标签文本"""
    parts = []
    if diary_type:
        parts.append(diary_type)
    if companion:
        parts.append(companion)
    if budget:
        parts.append(budget)
    return " ".join(parts)


def insert_diary_to_fts(diary_id: int, title: str, content_plain: str,
                         city_text: str = "", tag_text: str = ""):
    """向 FTS 虚拟表插入索引"""
    conn = _get_fts_conn()
    try:
        # 先删除旧记录（避免重复）
        conn.execute("DELETE FROM travel_diaries_fts WHERE rowid = ?", (diary_id,))
        conn.execute(
            """
            INSERT INTO travel_diaries_fts(rowid, title, content_plain, city_text, tag_text)
            VALUES (?, ?, ?, ?, ?)
            """,
            (diary_id, title or "", content_plain or "", city_text or "", tag_text or "")
        )
        conn.commit()
    except Exception as e:
        print(f"[FTS5] 插入索引失败 (diary_id={diary_id}): {e}")
        conn.rollback()
    finally:
        conn.close()


def update_diary_fts(diary_id: int, title: str, content_plain: str,
                      city_text: str = "", tag_text: str = ""):
    """更新 FTS 索引（先删后插）"""
    insert_diary_to_fts(diary_id, title, content_plain, city_text, tag_text)


def delete_diary_from_fts(diary_id: int):
    """从 FTS 索引删除"""
    conn = _get_fts_conn()
    try:
        conn.execute("DELETE FROM travel_diaries_fts WHERE rowid = ?", (diary_id,))
        conn.commit()
    except Exception as e:
        print(f"[FTS5] 删除索引失败 (diary_id={diary_id}): {e}")
        conn.rollback()
    finally:
        conn.close()


def _build_fuzzy_match(query: str) -> str:
    """
    构建模糊搜索 MATCH 表达式
    将查询拆成单个中文字符，用 OR 组合，支持部分匹配
    英文单词保持完整不做拆分
    """
    if not query.strip():
        return query
    
    chars = list(query.strip())
    # 用双引号包裹每个字符/词，防止 FTS5 特殊语法错误，然后用 OR 连接
    terms = [f'"{c}"' for c in chars]
    return " OR ".join(terms)


def search_diaries_fts(query: str, page: int = 1, page_size: int = 20,
                        sort: str = "relevance") -> dict:
    """
    FTS5 全文搜索（支持模糊搜索）
    
    Args:
        query: 搜索关键词
        page: 页码
        page_size: 每页数量
        sort: 排序方式 (relevance=按相关性, date=按时间, hot=按热度)
    
    Returns:
        {"total": int, "diaries": [...], "highlights": {...}}
    """
    conn = _get_fts_conn()
    try:
        # 先尝试 FTS5 精确 MATCH
        match_expr = query.strip()
        
        count_sql = """
            SELECT COUNT(*) FROM travel_diaries_fts
            WHERE travel_diaries_fts MATCH ?
        """
        try:
            cursor = conn.execute(count_sql, (match_expr,))
            total = cursor.fetchone()[0]
        except Exception:
            total = 0

        if total > 0:
            return _build_fts_results(conn, match_expr, page, page_size, sort)
        
        # 精确 MATCH 无结果时，尝试模糊 MATCH（拆字 OR 组合）
        fuzzy_expr = _build_fuzzy_match(query)
        if fuzzy_expr != match_expr:
            try:
                cursor = conn.execute(count_sql, (fuzzy_expr,))
                fuzzy_total = cursor.fetchone()[0]
                if fuzzy_total > 0:
                    return _build_fts_results(conn, fuzzy_expr, page, page_size, sort)
            except Exception:
                pass
        
        # FTS5 完全无结果时，使用 LIKE 降级搜索
        return _fallback_like_search(conn, query, page, page_size, sort)

    except Exception as e:
        print(f"[FTS5] 搜索失败: {e}")
        return {"total": 0, "diaries": [], "error": str(e)}
    finally:
        conn.close()


def _build_fts_results(conn, match_expr: str, page: int, page_size: int, sort: str) -> dict:
    """构建 FTS5 搜索结果"""
    if sort == "relevance":
        order_clause = "ORDER BY bm25(travel_diaries_fts, 10.0, 5.0, 2.0, 1.0) DESC"
    elif sort == "date":
        return _search_with_join(match_expr, page, page_size, "created_at")
    elif sort == "hot":
        return _search_with_join(match_expr, page, page_size, "hot")
    else:
        order_clause = "ORDER BY bm25(travel_diaries_fts) DESC"

    offset = (page - 1) * page_size
    search_sql = f"""
        SELECT rowid, title, content_plain,
               snippet(travel_diaries_fts, -1, '<em>', '</em>', '...', 60) as snippet_title,
               snippet(travel_diaries_fts, 1, '<em>', '</em>', '...', 120) as snippet_content,
               bm25(travel_diaries_fts, 10.0, 5.0, 2.0, 1.0) as score
        FROM travel_diaries_fts
        WHERE travel_diaries_fts MATCH ?
        {order_clause}
        LIMIT ? OFFSET ?
    """
    cursor = conn.execute(search_sql, (match_expr, page_size, offset))
    rows = cursor.fetchall()

    diaries = []
    for row in rows:
        diaries.append({
            "rowid": row["rowid"],
            "title": row["title"],
            "snippet_title": row["snippet_title"],
            "snippet_content": row["snippet_content"],
            "score": round(-row["score"], 4) if row["score"] else 0
        })

    return {
        "total": len(diaries),
        "diaries": diaries,
        "query": match_expr
    }


def _fallback_like_search(conn, query: str, page: int, page_size: int, sort: str) -> dict:
    """
    LIKE 降级搜索：当 FTS5 MATCH 无结果时，使用 LIKE 在 FTS 表中模糊搜索
    拆分成单个字符用 OR 组合，支持部分匹配
    """
    # 将查询拆成单个字符，每个字符做 LIKE 匹配，用 OR 连接
    chars = list(query.strip())
    conditions = " OR ".join([
        f"(title LIKE ? OR content_plain LIKE ? OR city_text LIKE ?)"
        for _ in chars
    ])
    params = [f"%{c}%" for _ in chars for __ in range(3)]
    
    count_sql = f"""
        SELECT COUNT(*) FROM travel_diaries_fts
        WHERE {conditions}
    """
    cursor = conn.execute(count_sql, params)
    total = cursor.fetchone()[0]
    
    if total == 0:
        return {"total": 0, "diaries": []}
    
    # 计算匹配字符数作为简单相关性排序
    offset = (page - 1) * page_size
    search_sql = f"""
        SELECT rowid, title, content_plain
        FROM travel_diaries_fts
        WHERE {conditions}
        ORDER BY rowid DESC
        LIMIT ? OFFSET ?
    """
    cursor = conn.execute(search_sql, (*params, page_size, offset))
    rows = cursor.fetchall()
    
    diaries = []
    for row in rows:
        # 生成简单高亮
        title = row["title"]
        content = row["content_plain"] or ""
        # 用完整查询尝试高亮，如果失败则用第一个匹配字符高亮
        snippet_title = _highlight_text(title, query)
        snippet_content = _highlight_text(content, query, max_len=120)
        if "<em>" not in snippet_title:
            for c in chars:
                snippet_title = _highlight_text(title, c)
                if "<em>" in snippet_title:
                    break
        if "<em>" not in snippet_content:
            for c in chars:
                snippet_content = _highlight_text(content, c, max_len=120)
                if "<em>" in snippet_content:
                    break
        
        # 计算匹配字符数作为分数
        matched_chars = sum(1 for c in chars if c in title or c in content)
        score = round(matched_chars / len(chars), 4) if chars else 0
        
        diaries.append({
            "rowid": row["rowid"],
            "title": title,
            "snippet_title": snippet_title,
            "snippet_content": snippet_content,
            "score": score
        })
    
    return {
        "total": total,
        "diaries": diaries,
        "query": query
    }


def _highlight_text(text: str, query: str, max_len: int = 60) -> str:
    """在文本中高亮匹配的关键词"""
    if not text or not query:
        return text or ""
    
    idx = text.find(query)
    if idx == -1:
        return text[:max_len] + ("..." if len(text) > max_len else "")
    
    # 截取匹配位置前后文本
    start = max(0, idx - 20)
    end = min(len(text), idx + len(query) + 40)
    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    
    # 高亮
    snippet = snippet.replace(query, f"<em>{query}</em>")
    return snippet


def _search_with_join(match_expr: str, page: int, page_size: int, order_by: str) -> dict:
    """
    搜索时 JOIN 回原表以支持日期/热度排序
    使用独立算法模块的 TopK 最小堆进行排序
    """
    from algorithms.diary_recommend import DiaryCandidate, topk_sort
    
    conn = _get_fts_conn()
    try:
        # 先获取所有匹配的 rowid + BM25 分数
        fts_sql = """
            SELECT rowid, bm25(travel_diaries_fts, 10.0, 5.0, 2.0, 1.0) as score
            FROM travel_diaries_fts
            WHERE travel_diaries_fts MATCH ?
        """
        cursor = conn.execute(fts_sql, (match_expr,))
        matched = [(row["rowid"], row["score"]) for row in cursor.fetchall()]

        if not matched:
            return {"total": 0, "diaries": []}

        total = len(matched)
        rowid_to_score = {r[0]: -r[1] for r in matched}
        matched_ids = [r[0] for r in matched]

        # JOIN 回 travel_diaries 获取完整信息
        placeholders = ",".join(["?"] * len(matched_ids))
        join_sql = f"""
            SELECT id, title, view_count, avg_rating, rating_count, created_at, diary_type, is_public, status
            FROM travel_diaries
            WHERE id IN ({placeholders})
            AND status = 'published'
            AND is_public = 1
        """
        cursor = conn.execute(join_sql, (*matched_ids,))
        rows = cursor.fetchall()
        
        # 转换为算法模块的候选对象
        candidates = []
        for row in rows:
            candidate = DiaryCandidate(
                id=row["id"],
                title=row["title"],
                view_count=row["view_count"] or 0,
                avg_rating=row["avg_rating"] or 0.0,
                rating_count=row["rating_count"] or 0,
                created_at=row["created_at"],
                diary_type=row["diary_type"] or "",
                fts_score=rowid_to_score.get(row["id"], 0)
            )
            candidates.append(candidate)
        
        # 根据排序方式调用不同算法
        if order_by == "created_at":
            candidates.sort(key=lambda x: x.created_at, reverse=True)
        elif order_by == "hot":
            # 使用独立算法模块的热度排序
            candidates.sort(key=lambda x: x.view_count * 0.7 + x.avg_rating * x.rating_count * 10, reverse=True)
        else:
            # 按 FTS 相关性排序
            candidates.sort(key=lambda x: x.fts_score, reverse=True)
        
        # 分页
        offset = (page - 1) * page_size
        paged = candidates[offset:offset + page_size]

        diaries = []
        for c in paged:
            diaries.append({
                "id": c.id,
                "title": c.title,
                "view_count": c.view_count,
                "avg_rating": round(c.avg_rating, 1) if c.avg_rating else 0,
                "rating_count": c.rating_count,
                "created_at": c.created_at,
                "score": c.fts_score
            })

        return {
            "total": total,
            "diaries": diaries
        }
    except Exception as e:
        print(f"[FTS5] JOIN 搜索失败: {e}")
        return {"total": 0, "diaries": []}
    finally:
        conn.close()


def search_by_exact_title(title: str) -> list:
    """
    标题精确查询：使用 normalized_title + title_hash
    
    返回匹配的日记 ID 列表
    """
    from models.database import get_db, TravelDiary
    from sqlalchemy.orm import Session

    normalized = normalize_title(title)
    title_hash = compute_title_hash(title)

    db: Session = next(get_db())
    try:
        # 先用 title_hash 快速缩小范围（O(1) 哈希查找）
        results = db.query(TravelDiary).filter(
            TravelDiary.title_hash == title_hash,
            TravelDiary.status == 'published'
        ).all()

        # 再精确比对 normalized_title
        matched = [d for d in results if d.normalized_title == normalized]
        return matched
    finally:
        db.close()


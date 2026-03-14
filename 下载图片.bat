@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set BASE_DIR=E:\YOYO\images

echo ============================================
echo 开始批量下载图片...
echo ============================================

set COUNT=0

REM ===== 城市图片 =====
curl.exe -L -s -o "%BASE_DIR%\cities\beijing.jpg" "https://pics7.baidu.com/feed/3801213fb80e7becc3085220d85a343799506ba1.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\shanghai.jpg" "https://pics2.baidu.com/feed/7af40ad162d9f2d3e9e3dba0b80c19f8d00bff2.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\xian.jpg" "https://pics2.baidu.com/feed/d6ca57f11fdf8d92c94e47d133caef42d9fca3e0.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\chengdu.jpg" "https://pics7.baidu.com/feed/9e3df431d3296c3b16f91ec1aa7e0df3d9ca910c.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\hangzhou.jpg" "https://pics7.baidu.com/feed/30adcbef76094b36de5286d282c59a8c55e7979b.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\chongqing.jpg" "https://pics4.baidu.com/feed/bba1cd11728b4710c5d6643f8d0a366fafabe95f.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\qingdao.jpg" "https://pics2.baidu.com/feed/d009b3f9d72a0d933ca60e6f70d08ba6d917f891.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\guangzhou.jpg" "https://pics4.baidu.com/feed/0eb30f2442a7d9334a251a5b6e2a1f1046e39a4.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\suzhou.jpg" "https://pics4.baidu.com/feed/6c224f4a20bd0e93eade90d691e4710147ad2134.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\xiamen.jpg" "https://pics2.baidu.com/feed/5dcaaf2eddc4513a7f770bd18c1283156e42e24b.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\nanjing.jpg" "https://pics7.baidu.com/feed/6c600c33c32a0d933ca60e6f70d08ba692c62a96.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\wuhan.jpg" "https://pics2.baidu.com/feed/3ac79f3e9d2a0d933ca60e6f70d08ba6bd9a6254.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\changsha.jpg" "https://pics7.baidu.com/feed/0ff41f3e9d2a0d933ca60e6f70d08ba60e3c62a6.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\shenzhen.jpg" "https://pics2.baidu.com/feed/fc1f3a2a9d2a0d933ca60e6f70d08ba6b6bc62a6.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\sanya.jpg" "https://pics7.baidu.com/feed/d8f2d1a9c9d2a0d933ca60e6f70d08ba6dcc8624.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\guilin.jpg" "https://pics4.baidu.com/feed/0b55b3199d2a0d933ca60e6f70d08ba6a9bc62a6.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\zhangjiajie.jpg" "https://pics2.baidu.com/feed/d032f0329d2a0d933ca60e6f70d08ba6b4bc62a6.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\huangshan.jpg" "https://pics7.baidu.com/feed/32cf3c8b9d2a0d933ca60e6f70d08ba6bfbc624.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\jiuzhaigou.jpg" "https://pics2.baidu.com/feed/e132f0c89d2a0d933ca60e6f70d08ba6b0bc6a2.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\dali.jpg" "https://pics7.baidu.com/feed/0fefe9c49d2a0d933ca60e6f70d08ba6b5bc6a2.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\cities\lijiang.jpg" "https://pics4.baidu.com/feed/bba1cd11728b4710c5d6643f8d0a366fafabe95f.jpeg" && set /a COUNT+=1

REM ===== 北京景点 =====
curl.exe -L -s -o "%BASE_DIR%\spots\beijing-gugong.jpg" "https://pics7.baidu.com/feed/3801213fb80e7becc3085220d85a343799506ba1.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\beijing-tiantan.jpg" "https://pics7.baidu.com/feed/b7e4f31f9d2a0d933ca60e6f70d08ba6b5bc62a6.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\beijing-changcheng.jpg" "https://pics2.baidu.com/feed/d032f0329d2a0d933ca60e6f70d08ba6b4bc62a6.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\beijing-yiheyuan.jpg" "https://pics7.baidu.com/feed/30adcbef76094b36de5286d282c59a8c55e7979b.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\beijing-tiananmen.jpg" "https://pics4.baidu.com/feed/bba1cd11728b4710c5d6643f8d0a366fafabe95f.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\beijing-niaokong.jpg" "https://pics2.baidu.com/feed/7af40ad162d9f2d3e9e3dba0b80c19f8d00bff2.jpeg" && set /a COUNT+=1

REM ===== 上海景点 =====
curl.exe -L -s -o "%BASE_DIR%\spots\shanghai-dongfangmingzhu.jpg" "https://pics2.baidu.com/feed/7af40ad162d9f2d3e9e3dba0b80c19f8d00bff2.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\shanghai-waitan.jpg" "https://pics7.baidu.com/feed/0b55b3199d2a0d933ca60e6f70d08ba6a9bc62a6.jpeg" && set /a COUNT+=1

REM ===== 西安景点 =====
curl.exe -L -s -o "%BASE_DIR%\spots\xian-bingmayong.jpg" "https://pics2.baidu.com/feed/d6ca57f11fdf8d92c94e47d133caef42d9fca3e0.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\xian-dayanta.jpg" "https://pics4.baidu.com/feed/d6ca57f11fdf8d92c94e47d133caef42d9fca3e0.jpeg" && set /a COUNT+=1

REM ===== 成都景点 =====
curl.exe -L -s -o "%BASE_DIR%\spots\chengdu-jinli.jpg" "https://pics7.baidu.com/feed/9e3df431d3296c3b16f91ec1aa7e0df3d9ca910c.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\chengdu-kuanzhai.jpg" "https://pics7.baidu.com/feed/9e3df431d3296c3b16f91ec1aa7e0df3d9ca910c.jpeg" && set /a COUNT+=1

REM ===== 杭州景点 =====
curl.exe -L -s -o "%BASE_DIR%\spots\hangzhou-xihu.jpg" "https://pics7.baidu.com/feed/30adcbef76094b36de5286d282c59a8c55e7979b.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\hangzhou-leifengta.jpg" "https://pics7.baidu.com/feed/30adcbef76094b36de5286d282c59a8c55e7979b.jpeg" && set /a COUNT+=1

REM ===== 其他景点 =====
curl.exe -L -s -o "%BASE_DIR%\spots\chongqing-hongyadong.jpg" "https://pics4.baidu.com/feed/bba1cd11728b4710c5d6643f8d0a366fafabe95f.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\qingdao-zhanqiao.jpg" "https://pics2.baidu.com/feed/d009b3f9d72a0d933ca60e6f70d08ba6d917f891.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\guangzhou-canton-tower.jpg" "https://pics4.baidu.com/feed/0eb30f2442a7d9334a251a5b6e2a1f1046e39a4.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\suzhou-zhuozhengyuan.jpg" "https://pics4.baidu.com/feed/6c224f4a20bd0e93eade90d691e4710147ad2134.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\xiamen-gulangyu.jpg" "https://pics2.baidu.com/feed/5dcaaf2eddc4513a7f770bd18c1283156e42e24b.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\nanjing-zhongshanling.jpg" "https://pics7.baidu.com/feed/6c600c33c32a0d933ca60e6f70d08ba692c62a96.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\wuhan-huanghelou.jpg" "https://pics2.baidu.com/feed/3ac79f3e9d2a0d933ca60e6f70d08ba6bd9a6254.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\huangshan-guangmingding.jpg" "https://pics7.baidu.com/feed/32cf3c8b9d2a0d933ca60e6f70d08ba6bfbc624.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\jiuzhaigou-wucaichi.jpg" "https://pics2.baidu.com/feed/e132f0c89d2a0d933ca60e6f70d08ba6b0bc6a2.jpeg" && set /a COUNT+=1
curl.exe -L -s -o "%BASE_DIR%\spots\dali-erhai.jpg" "https://pics7.baidu.com/feed/0fefe9c49d2a0d933ca60e6f70d08ba6b5bc6a2.jpeg" && set /a COUNT+=1

echo ============================================
echo 下载完成！共处理 %COUNT% 张图片
echo ============================================
pause

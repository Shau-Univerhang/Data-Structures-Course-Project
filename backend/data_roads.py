"""
Add more road edge data - reach 200+
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import SessionLocal, RoadNode, RoadEdge, ScenicSpot

def add_road_data():
    """Add road data for more scenic spots"""
    db = SessionLocal()
    
    # Get some popular spots
    spots = db.query(ScenicSpot).limit(30).all()
    
    for spot in spots:
        # Check if road data already exists
        existing_nodes = db.query(RoadNode).filter(RoadNode.spot_id == spot.id).count()
        if existing_nodes > 0:
            continue
        
        # Create road nodes for each spot
        nodes = []
        node_names = ["entrance", "square", "main_hall", "pavilion", "center", "parking", "exit"]
        
        for i, name in enumerate(node_names):
            node = RoadNode(
                spot_id=spot.id,
                name=f"{spot.name[:4]}-{name}",
                location_lat=spot.location_lat + (i * 0.001) if spot.location_lat else 0,
                location_lng=spot.location_lng + (i * 0.001) if spot.location_lng else 0,
                node_type="entrance" if i == 0 else ("exit" if i == len(node_names)-1 else "building")
            )
            db.add(node)
            nodes.append(node)
        
        db.commit()
        
        # Create road edges (connect adjacent nodes to form a loop)
        for i in range(len(nodes)):
            from_node = nodes[i]
            to_node = nodes[(i + 1) % len(nodes)]
            
            edge = RoadEdge(
                spot_id=spot.id,
                from_node_id=from_node.id,
                to_node_id=to_node.id,
                distance=100 + i * 20,
                road_type="walk",
                is_bidirectional=True
            )
            db.add(edge)
        
        db.commit()
        print(f"Added road data for: {spot.name}")
    
    # Statistics
    node_count = db.query(RoadNode).count()
    edge_count = db.query(RoadEdge).count()
    print(f"\nTotal nodes: {node_count}")
    print(f"Total edges: {edge_count}")
    
    db.close()


if __name__ == "__main__":
    add_road_data()

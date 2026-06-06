from app.services.search import search_engine

def run_index_export():
    print("Exporting vector indices to persistent local files...")
    search_engine.save_indexes()
    print("Vector indices exported successfully.")

if __name__ == "__main__":
    run_index_export()

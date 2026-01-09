import numpy as np

def compute_cosine_similarity(embed1, embed2):
    """
    Computes cosine similarity between two embeddings.
    """
    # Ensure they are numpy arrays
    e1 = np.array(embed1)
    e2 = np.array(embed2)

    norm1 = np.linalg.norm(e1)
    norm2 = np.linalg.norm(e2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return np.dot(e1, e2) / (norm1 * norm2)

def find_best_match(target_embedding, references, threshold=0.4):
    """
    Finds the best match for target_embedding in references.
    
    references: List of dicts, e.g. [{"id": "1", "embedding": [...]}, ...]
                OR just a list of embeddings (though we need IDs to be useful).
                
    Returns:
        {
            "match": bool,
            "best_match_id": str or None,
            "score": float
        }
    """
    best_score = -1.0
    best_id = None

    for ref in references:
        # Handle cases where ref is dict or just list
        if isinstance(ref, dict):
            ref_emb = ref.get("embedding")
            ref_id = ref.get("id", "unknown")
        else:
            ref_emb = ref
            ref_id = "unknown"

        if ref_emb is None:
            continue

        score = compute_cosine_similarity(target_embedding, ref_emb)
        
        if score > best_score:
            best_score = score
            best_id = ref_id

    is_match = best_score > threshold
    
    return {
        "match": is_match,
        "best_match_id": best_id if is_match else None,
        "score": float(best_score)
    }

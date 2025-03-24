# Firestore Queries for Gray Swan Project

This document lists *every* Firestore query used by the Gray Swan project, along with the supporting Firestore index.

**Important Notes:**

*   `db` refers to the initialized Firestore client instance (e.g., `db = firestore.client()`).
*   All queries are assumed to be *asynchronous* (using `await`).
*   Pagination is *not* explicitly shown in all queries, but *all* queries that return multiple documents *must* implement pagination using `limit()` and `start_after()`.  See the helper functions in `firestore_manager.py` for the implementation.
*    Error handling (try-except) is not included in the example queries to keep the file consise.

## Prompts Collection (`prompts`)

### Get Single Prompt

1.  **Get prompt by ID:**

    ```python
    db.collection('prompts').document(prompt_id).get()
    ```

    *   *Supported by:* Firestore automatically indexes document IDs. No composite index needed.

2.  **Get prompt by hash:**

    ```python
    db.collection('prompts').where('prompt_hash', '==', prompt_hash).get()
    ```

    *   *Supported by:*  `prompts`: `prompt_hash` (Ascending), `__name__` (Ascending)

### Get Multiple Prompts (with Filtering)

3.  **Get all prompts for a specific category:**

    ```python
    db.collection('prompts').where('category', '==', category).order_by('creation_timestamp').get()
    ```

    *   *Supported by:* `prompts`: `category` (Ascending), `creation_timestamp` (Ascending), `__name__` (Ascending)  *(You already have a similar index. Confirm the order.)*

4.  **Get all prompts for a specific category and technique:**

    ```python
    db.collection('prompts').where('category', '==', category).where('techniques_used', 'array_contains', technique).get()
    ```

    *   *Supported by:* `prompts`: `category` (Ascending), `techniques_used` (Array)  *(You'll need the array index on `techniques_used`.)*

5.  **Get all prompts for a specific challenge ID:**

    ```python
    db.collection('prompts').where('challenge_id', '==', challenge_id).get()
    ```

    *   *Supported by:* `prompts`: `challenge_id` (Ascending), `__name__` (Ascending)

6.  **Get all prompts (no filtering):**

    ```python
    db.collection('prompts').order_by('creation_timestamp').get()  # Usually with limit() and start_after()
    ```

    *   *Supported by:* Firestore automatically indexes `creation_timestamp`.

7.  **Get prompts created after a specific timestamp:**

    ```python
    db.collection('prompts').where('creation_timestamp', '>', timestamp).order_by('creation_timestamp').get()
    ```

    *   *Supported by:* Firestore automatically indexes `creation_timestamp`.

8.  **Get all prompts for a specific Gray Swan version and category:**

    ```python
    db.collection('prompts').where('gray_swan_version', '==', version).where('category', '==', category).get()
    ```

    *   *Supported by:* `prompts`: `gray_swan_version` (Ascending), `category` (Ascending), `__name__` (Ascending)

9.  **Get all prompts that use a specific technique (using `techniques_used` array):**

    ```python
    db.collection('prompts').where('techniques_used', 'array_contains', technique).get()
    ```

    *   *Supported by:* `prompts`: `techniques_used` (Array)  *(Firestore's special array index)*

10. **Get all prompts with specific category created after a timestamp:**

    ```python
    db.collection('prompts').where('category', '==', category).where('creation_timestamp', '>', timestamp).order_by('creation_timestamp').get()
    ```
    *   *Supported by:* `prompts`: `category` (Ascending), `creation_timestamp` (Ascending), `__name__` (Ascending)
## Benchmark Results Collection (`benchmark_results`)

### Get Single Result

*(There's no direct "get by ID" here, as you'll likely always be querying for results based on other criteria.  Firestore automatically indexes the document ID, so if you *do* need to get a result by its auto-generated ID, you can use `db.collection('benchmark_results').document(result_id).get()`.)*

### Get Multiple Results (with Filtering)

11. **Get all benchmark results for a specific prompt ID:**

    ```python
    db.collection('benchmark_results').where('prompt_id', '==', prompt_id).get()
    ```

    *   *Supported by:* `benchmark_results`: `prompt_id` (Ascending), `__name__` (Ascending)

12. **Get all benchmark results for a specific model:**

    ```python
    db.collection('benchmark_results').where('model_name', '==', model_name).get()
    ```

    *   *Supported by:* Firestore automatically indexes `model_name`.

13. **Get all benchmark results for a specific run ID:**

    ```python
    db.collection('benchmark_results').where('run_id', '==', run_id).get()
    ```

    *   *Supported by:* `benchmark_results`: `run_id` (Ascending), `__name__` (Ascending)

14. **Get all benchmark results for a specific model and category:**

    ```python
    db.collection('benchmark_results').where('model_name', '==', model_name).where('category', '==', category).get()
    ```

    *   *Supported by:* `benchmark_results`: `model_name` (Ascending), `category` (Ascending), `__name__` (Ascending)

15. **Get all benchmark results for a specific prompt ID, model, and category:**

    ```python
        db.collection('benchmark_results').where('prompt_id', '==', prompt_id).where('model_name', '==', model_name).where('category', '==', category).get()
    ```

    *  Supported by:* `benchmark_results`: `prompt_id` (Ascending), `model_name` (Ascending), `category` (Ascending), `__name__` (Ascending)

16. **Get all benchmark results for a specific technique and success status:**

    ```python
        db.collection('benchmark_results').where('technique', '==', technique).where('success', '==', success_status).get()

    ```

    * Supported by:* `benchmark_results`: `technique` (Ascending), `success` (Ascending), `__name__` (Ascending)

17. **Get all benchmark results for a specific Gray Swan version and model:**
    ```python
    db.collection('benchmark_results').where('gray_swan_version', '==', version).where('model_name', '==', model_name).get()
    ```

    *   *Supported by:* `benchmark_results`: `gray_swan_version` (Ascending), `model_name` (Ascending), `__name__` (Ascending)

18. **Get all benchmark results for a specific model, category, and success status:**

    ```python
    db.collection('benchmark_results').where('model_name', '==', model_name).where('category', '==', category).where('success', '==', success_status).get()
    ```

     *   *Supported by:* `benchmark_results`: `model_name` (Ascending), `category` (Ascending), `success` (Ascending), `__name__` (Ascending)

### Aggregation Queries (Calculated in Code)

19. **Get average success rate for a specific model and category:**

    ```python
    # Fetch all matching documents:
    query = db.collection('benchmark_results').where('model_name', '==', model_name).where('category', '==', category)
    results = await query.get()

    # Calculate the average in Python:
    total_score = 0
    count = 0
    for doc in results:
        result_data = doc.to_dict()
        total_score += result_data.get('success_score', 0.0)  # Use .get() to handle missing data
        count += 1

    average_success_rate = total_score / count if count > 0 else 0.0
    ```

    *   *Supported by:* `benchmark_results`: `model_name` (Ascending), `category` (Ascending), `__name__` (Ascending)
    *   *Note:* Firestore does *not* have built-in aggregation functions like `AVG`. You need to fetch the relevant documents and calculate the average in your Python code.

---

**Key Considerations and Next Steps:**

*   **Completeness:** Review this list *very carefully*.  Think through *all* the ways you might need to query your data, both now and in the future.  Add any missing queries.
*   **Index Creation:**  Use this `QUERIES.md` file as your guide for creating composite indexes in the Firebase console.
*   **Pagination:** Remember that *all* of these queries that return multiple documents *must* be implemented with pagination in your `firestore_manager.py` helper functions.
*   **Testing:**  As you implement your helper functions, write unit tests that execute these queries against a *local* Firestore emulator (to avoid using your credits during testing).
* **Living Document:** This document should be updated whenever the database needs to be changed or queried.

This comprehensive `QUERIES.md` file is a critical piece of your Firebase integration. It ensures you have the right indexes and provides a clear roadmap for implementing your data access logic.
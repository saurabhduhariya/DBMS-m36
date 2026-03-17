# src/module_36/tests/test_service.py
# Unit tests for Module 36 service layer.
# MongoDB is mocked — no live connection required.
import unittest
from unittest.mock import MagicMock, patch, call
from datetime import datetime
import pymongo.errors


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _make_db():
    """Return a MagicMock that looks like a pymongo Database."""
    db = MagicMock()
    return db


# ═══════════════════════════════════════════════════════════════════════════════
# init_db
# ═══════════════════════════════════════════════════════════════════════════════

class TestInitDb(unittest.TestCase):

    @patch("src.module_36.service.init_collections")
    def test_returns_true_on_success(self, mock_init):
        """init_db() should call init_collections and return True."""
        from src.module_36.service import init_db
        result = init_db()
        mock_init.assert_called_once()
        self.assertTrue(result)

    @patch("src.module_36.service.init_collections", side_effect=pymongo.errors.ConnectionFailure("down"))
    def test_raises_runtime_error_on_connection_failure(self, _mock):
        """init_db() should raise RuntimeError when MongoDB is unreachable."""
        from src.module_36.service import init_db
        with self.assertRaises(RuntimeError) as ctx:
            init_db()
        self.assertIn("connection failed", str(ctx.exception).lower())

    @patch("src.module_36.service.init_collections")
    def test_seeds_correct_number_of_records(self, mock_init):
        """
        Verifies that init_collections is responsible for seeding.
        We check that it is called exactly once (implying full seeding).
        """
        from src.module_36.service import init_db
        init_db()
        self.assertEqual(mock_init.call_count, 1)


# ═══════════════════════════════════════════════════════════════════════════════
# find_similar_patients
# ═══════════════════════════════════════════════════════════════════════════════

def _build_patient(pid, age, gender, blood_group):
    return {
        "patient_id": pid, "age": age, "gender": gender,
        "blood_group": blood_group, "address": "Test City",
        "lifestyle_data": "non-smoker,active"
    }


def _build_match_result(pid, score):
    return {
        "patient_id": pid, "age": 45, "gender": "Male",
        "blood_group": "O+", "address": "Delhi",
        "severity_level": 7, "symptom_vector": "7,3,8,5,2",
        "similarity_score": score,
        "treatment": "Chemotherapy", "survival_rate": 85.0,
        "prognosis_data": "Stage II"
    }


class TestFindSimilarPatients(unittest.TestCase):

    def _patch_db(self, db_mock):
        patcher = patch("src.module_36.service.get_db", return_value=db_mock)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_returns_empty_list_for_empty_database(self):
        """find_similar_patients() should return [] when there are no patients."""
        db = _make_db()
        db.patient_profiles.aggregate.return_value = iter([])  # no stats
        self._patch_db(db)

        from src.module_36.service import find_similar_patients
        result = find_similar_patients(source_pid=1)
        self.assertEqual(result, [])

    def test_returns_empty_list_when_patient_not_found(self):
        """find_similar_patients() should return [] when source patient doesn't exist."""
        db = _make_db()
        # Stats exist (other patients present), but source patient is missing
        db.patient_profiles.aggregate.return_value = iter([
            {"_id": None, "min_age": 25, "max_age": 70}
        ])
        db.patient_profiles.find_one.return_value = None   # patient not found
        db.clinical_cases.find_one.return_value = None
        self._patch_db(db)

        from src.module_36.service import find_similar_patients
        result = find_similar_patients(source_pid=999)
        self.assertEqual(result, [])

    def test_returns_ranked_results_sorted_by_score(self):
        """find_similar_patients() should return results ordered by similarity_score desc."""
        db = _make_db()

        # First aggregate call → stats; second → ranked matches
        ranked = [
            _build_match_result(6, 0.9200),
            _build_match_result(10, 0.8700),
            _build_match_result(3, 0.7500),
        ]
        db.patient_profiles.aggregate.side_effect = [
            iter([{"_id": None, "min_age": 25, "max_age": 70}]),
            iter(ranked),
        ]
        db.patient_profiles.find_one.return_value = _build_patient(1, 45, "Male", "O+")
        db.clinical_cases.find_one.return_value = {"patient_id": 1, "severity_level": 7}
        self._patch_db(db)

        from src.module_36.service import find_similar_patients
        results = find_similar_patients(source_pid=1)

        self.assertEqual(len(results), 3)
        scores = [r["similarity_score"] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_raises_on_connection_failure(self):
        """find_similar_patients() should raise RuntimeError when MongoDB is down."""
        db = _make_db()
        db.patient_profiles.aggregate.side_effect = pymongo.errors.ConnectionFailure("down")
        self._patch_db(db)

        from src.module_36.service import find_similar_patients
        with self.assertRaises(RuntimeError) as ctx:
            find_similar_patients(source_pid=1)
        self.assertIn("unreachable", str(ctx.exception).lower())


# ═══════════════════════════════════════════════════════════════════════════════
# submit_feedback
# ═══════════════════════════════════════════════════════════════════════════════

class TestSubmitFeedback(unittest.TestCase):

    def _patch_db(self, db_mock):
        patcher = patch("src.module_36.service.get_db", return_value=db_mock)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _setup_db(self, match_exists=True, existing_feedbacks=None):
        db = _make_db()
        db.similarity_matches.find_one.return_value = (
            {"match_id": 1, "confidence_score": 0.8} if match_exists else None
        )
        db.feedback.find_one.return_value = (
            {"feedback_id": 3} if existing_feedbacks else None
        )
        db.feedback.aggregate.return_value = iter([
            {"_id": None, "avg_useful": 0.75}
        ])
        return db

    def test_returns_true_on_success(self):
        db = self._setup_db()
        self._patch_db(db)

        from src.module_36.service import submit_feedback
        result = submit_feedback(match_id=1, is_useful=True)
        self.assertTrue(result)

    def test_inserts_feedback_document(self):
        db = self._setup_db()
        self._patch_db(db)

        from src.module_36.service import submit_feedback
        submit_feedback(match_id=1, is_useful=True, doctor_comments="Good match")

        db.feedback.insert_one.assert_called_once()
        inserted = db.feedback.insert_one.call_args[0][0]
        self.assertEqual(inserted["match_id"], 1)
        self.assertTrue(inserted["is_useful"])
        self.assertEqual(inserted["doctor_comments"], "Good match")

    def test_updates_confidence_score_after_insert(self):
        """Trigger equivalent: confidence_score must be updated after feedback insert."""
        db = self._setup_db()
        self._patch_db(db)

        from src.module_36.service import submit_feedback
        submit_feedback(match_id=1, is_useful=True)

        db.similarity_matches.update_one.assert_called_once_with(
            {"match_id": 1},
            {"$set": {"confidence_score": 0.75}}
        )

    def test_raises_value_error_for_nonexistent_match(self):
        """Edge case: feedback for a match_id that doesn't exist should raise ValueError."""
        db = self._setup_db(match_exists=False)
        self._patch_db(db)

        from src.module_36.service import submit_feedback
        with self.assertRaises(ValueError) as ctx:
            submit_feedback(match_id=999, is_useful=True)
        self.assertIn("999", str(ctx.exception))

    def test_raises_runtime_error_on_connection_failure(self):
        db = _make_db()
        db.similarity_matches.find_one.side_effect = pymongo.errors.ConnectionFailure("down")
        self._patch_db(db)

        from src.module_36.service import submit_feedback
        with self.assertRaises(RuntimeError):
            submit_feedback(match_id=1, is_useful=True)

    def test_auto_increments_feedback_id(self):
        """feedback_id should be last_id + 1."""
        db = self._setup_db(existing_feedbacks=True)
        self._patch_db(db)

        from src.module_36.service import submit_feedback
        submit_feedback(match_id=1, is_useful=False)

        inserted = db.feedback.insert_one.call_args[0][0]
        self.assertEqual(inserted["feedback_id"], 4)  # last was 3, so next is 4


# ═══════════════════════════════════════════════════════════════════════════════
# get_dashboard_view
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetDashboardView(unittest.TestCase):

    def _patch_db(self, db_mock):
        patcher = patch("src.module_36.service.get_db", return_value=db_mock)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_returns_list_of_joined_records(self):
        """get_dashboard_view() should return all fields from the multi-$lookup pipeline."""
        expected = [
            {
                "match_id": 1,
                "source_id": 1, "source_age": 45, "source_gender": "Male",
                "matched_id": 6, "matched_age": 47, "matched_gender": "Male",
                "similarity_score": 0.92, "confidence_score": 0.75,
                "treatment": "Chemotherapy", "survival_rate": 78.0,
                "feedback_count": 2
            }
        ]
        db = _make_db()
        db.similarity_matches.aggregate.return_value = iter(expected)
        self._patch_db(db)

        from src.module_36.service import get_dashboard_view
        result = get_dashboard_view()

        self.assertEqual(len(result), 1)
        row = result[0]
        self.assertIn("match_id", row)
        self.assertIn("source_id", row)
        self.assertIn("matched_id", row)
        self.assertIn("similarity_score", row)
        self.assertIn("feedback_count", row)

    def test_returns_empty_list_when_no_matches(self):
        """get_dashboard_view() should return [] when similarity_matches is empty."""
        db = _make_db()
        db.similarity_matches.aggregate.return_value = iter([])
        self._patch_db(db)

        from src.module_36.service import get_dashboard_view
        result = get_dashboard_view()
        self.assertEqual(result, [])

    def test_raises_runtime_error_on_connection_failure(self):
        db = _make_db()
        db.similarity_matches.aggregate.side_effect = pymongo.errors.ConnectionFailure("down")
        self._patch_db(db)

        from src.module_36.service import get_dashboard_view
        with self.assertRaises(RuntimeError) as ctx:
            get_dashboard_view()
        self.assertIn("unreachable", str(ctx.exception).lower())

    def test_joins_all_four_collections(self):
        """Verify the aggregation pipeline touches all required collections."""
        db = _make_db()
        db.similarity_matches.aggregate.return_value = iter([])
        self._patch_db(db)

        from src.module_36.service import get_dashboard_view
        get_dashboard_view()

        pipeline_arg = db.similarity_matches.aggregate.call_args[0][0]
        from_collections = [
            stage["$lookup"]["from"]
            for stage in pipeline_arg
            if "$lookup" in stage
        ]
        self.assertIn("patient_profiles", from_collections)
        self.assertIn("prognosis", from_collections)
        self.assertIn("feedback", from_collections)


# ═══════════════════════════════════════════════════════════════════════════════
# Edge-case tests for get_all_patients / get_collection_data
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases(unittest.TestCase):

    def _patch_db(self, db_mock):
        patcher = patch("src.module_36.service.get_db", return_value=db_mock)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_all_patients_empty_db(self):
        """get_all_patients() returns [] when collection is empty."""
        db = _make_db()
        db.patient_profiles.find.return_value.sort.return_value = iter([])
        self._patch_db(db)

        from src.module_36.service import get_all_patients
        result = get_all_patients()
        self.assertEqual(result, [])

    def test_get_all_patients_network_timeout(self):
        """get_all_patients() raises RuntimeError on network timeout."""
        db = _make_db()
        db.patient_profiles.find.side_effect = pymongo.errors.ServerSelectionTimeoutError("timeout")
        self._patch_db(db)

        from src.module_36.service import get_all_patients
        with self.assertRaises(RuntimeError):
            get_all_patients()

    def test_get_collection_data_invalid_collection(self):
        """get_collection_data() raises RuntimeError on OperationFailure."""
        db = _make_db()
        db.__getitem__.return_value.find.side_effect = pymongo.errors.OperationFailure("denied")
        self._patch_db(db)

        from src.module_36.service import get_collection_data
        with self.assertRaises(RuntimeError):
            get_collection_data("nonexistent_collection")


if __name__ == "__main__":
    unittest.main()

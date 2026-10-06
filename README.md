# aidd-ci-demo

A small clinic appointment app with a pytest suite, used to show GitHub Actions in BUS X501 (Session 17).

Every push runs the tests in `.github/workflows/tests.yml`. A green check next to a commit means all 15 tests passed on a clean machine. A red X means at least one failed.

To run the tests on your own computer:

```
pip install -r requirements.txt
cd clinic_app
python -m pytest
```

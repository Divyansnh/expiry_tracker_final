# Setup Scripts Verification Guide

This guide explains how to verify that your setup scripts are working properly without affecting your main application.

## 🎯 Why Verify Setup Scripts?

Before sharing your repository with others, it's crucial to ensure that your setup scripts work correctly. This prevents users from encountering issues when trying to set up your application.

## 📋 Available Verification Methods

### 1. **Quick Verification** (Recommended First Step)
```bash
python scripts/verify_setup.py
```
**What it does:**
- ✅ Checks if all required files exist
- ✅ Validates script syntax
- ✅ Tests help commands
- ✅ Verifies permissions
- ✅ Confirms documentation exists

**When to use:** Before sharing your repository or after making changes to setup scripts.

### 2. **Dry Run Testing** (Safe Testing)
```bash
python scripts/quick_test.py --dry-run
```
**What it does:**
- ✅ Tests script syntax without execution
- ✅ Validates help commands
- ✅ Simulates test environment creation
- ✅ No actual setup operations performed

**When to use:** When you want to test the scripts without any side effects.

### 3. **Full Testing** (Complete Verification)
```bash
python scripts/quick_test.py
```
**What it does:**
- ✅ Creates isolated test environment
- ✅ Runs actual setup scripts in isolation
- ✅ Tests both Python and shell scripts
- ✅ Validates complete setup process
- ✅ Automatically cleans up test environment

**When to use:** When you want to fully verify that the setup process works end-to-end.

## 🔍 What Each Test Checks

### File Structure Tests
- [ ] `requirements.txt` exists
- [ ] `run.py` exists
- [ ] `app/__init__.py` exists
- [ ] `app/config.py` exists
- [ ] `migrations/env.py` exists
- [ ] `scripts/` directory exists

### Setup Script Tests
- [ ] `scripts/setup.py` exists and has valid Python syntax
- [ ] `scripts/setup.sh` exists and has valid shell syntax
- [ ] Shell script has execute permissions
- [ ] Both scripts respond to `--help` command
- [ ] Scripts can run without critical errors

### Test Script Tests
- [ ] `scripts/quick_test.py` exists and has valid syntax
- [ ] Test script can create isolated environments
- [ ] Test script can clean up after itself

### Documentation Tests
- [ ] `scripts/README.md` exists
- [ ] `README.md` exists and mentions setup scripts

## 🚀 Verification Workflow

### Step 1: Quick Verification
```bash
python scripts/verify_setup.py
```
This should show "ALL CHECKS PASSED!" with 100% success rate.

### Step 2: Dry Run Test
```bash
python scripts/quick_test.py --dry-run
```
This should show all tests passing without any actual execution.

### Step 3: Full Test (Optional)
```bash
python scripts/quick_test.py
```
This will actually run the setup scripts in an isolated environment.

## 📊 Expected Results

### Successful Verification Output
```
🔍 Verifying Setup Scripts
This script checks if your setup scripts are ready for use.

=== Checking Required Files ===
[SUCCESS] ✓ Requirements file exists
[SUCCESS] ✓ Application entry point exists
[SUCCESS] ✓ Flask application factory exists
[SUCCESS] ✓ Configuration file exists
[SUCCESS] ✓ Database migrations exists

=== Checking Required Directories ===
[SUCCESS] ✓ Application directory exists
[SUCCESS] ✓ Migrations directory exists
[SUCCESS] ✓ Scripts directory exists

=== Checking Setup Scripts ===
[SUCCESS] ✓ Python setup script exists
[SUCCESS] ✓ setup.py syntax is valid
[SUCCESS] ✓ setup.py help command works
[SUCCESS] ✓ Shell setup script exists
[SUCCESS] ✓ setup.sh syntax is valid
[SUCCESS] ✓ setup.sh is executable
[SUCCESS] ✓ setup.sh help command works

=== Checking Test Scripts ===
[SUCCESS] ✓ Quick test script exists
[SUCCESS] ✓ quick_test.py syntax is valid

=== Checking Documentation ===
[SUCCESS] ✓ Scripts documentation exists
[SUCCESS] ✓ Main README exists

==================================================
VERIFICATION SUMMARY
==================================================
🎉 ALL CHECKS PASSED!
Passed: 19/19 (100.0%)
Your setup scripts are ready for use!

Next steps:
1. Test the scripts: python scripts/quick_test.py
2. Share your repository with others
3. Users can run: python scripts/setup.py
```

### Successful Test Output
```
🚀 Starting Quick Setup Script Tests
Dry run: False

[INFO] Testing script syntax...
[SUCCESS] ✓ Python script syntax is valid
[SUCCESS] ✓ Shell script syntax is valid

[INFO] Testing help commands...
[SUCCESS] ✓ Python script help command works
[SUCCESS] ✓ Shell script help command works

[INFO] Testing setup scripts in isolated environment...
[INFO] Created test environment: /tmp/expiry_tracker_test_abc123
[INFO] Copied requirements.txt to test environment
[INFO] Copied run.py to test environment
[INFO] Copied app to test environment
[INFO] Copied migrations to test environment
[INFO] Copied scripts to test environment
[INFO] Testing Python setup script...
[SUCCESS] ✓ Python setup script test passed
[INFO] Testing shell setup script...
[SUCCESS] ✓ Shell setup script test passed
[INFO] Cleaned up test environment: /tmp/expiry_tracker_test_abc123

==================================================
TEST RESULTS SUMMARY
==================================================
🎉 ALL TESTS PASSED!
Passed: 3/3
Your setup scripts are working correctly!
```

## ⚠️ Common Issues and Solutions

### Issue: "Script not found" errors
**Solution:** Ensure you're running the verification from the project root directory.

### Issue: "Permission denied" for shell script
**Solution:** Make the script executable:
```bash
chmod +x scripts/setup.sh
```

### Issue: "Syntax error" in Python script
**Solution:** Check for Python syntax issues in the setup script.

### Issue: "Help command failed"
**Solution:** Ensure the script has proper argument parsing with `argparse`.

### Issue: "Test environment creation failed"
**Solution:** Check disk space and permissions in the temp directory.

## 🔧 Manual Verification Steps

If the automated tests fail, you can manually verify:

1. **Check file existence:**
   ```bash
   ls -la scripts/
   ls -la requirements.txt run.py app/ migrations/
   ```

2. **Test Python syntax:**
   ```bash
   python -m py_compile scripts/setup.py
   python -m py_compile scripts/quick_test.py
   ```

3. **Test shell syntax:**
   ```bash
   bash -n scripts/setup.sh
   ```

4. **Test help commands:**
   ```bash
   python scripts/setup.py --help
   ./scripts/setup.sh --help
   ```

5. **Test permissions:**
   ```bash
   ls -la scripts/setup.sh
   ```

## 📝 Pre-Release Checklist

Before sharing your repository, ensure:

- [ ] `python scripts/verify_setup.py` shows 100% success
- [ ] `python scripts/quick_test.py --dry-run` passes all tests
- [ ] `python scripts/quick_test.py` passes all tests (optional but recommended)
- [ ] All documentation is up to date
- [ ] `.gitignore` includes all necessary exclusions
- [ ] README.md includes setup instructions

## 🎯 Best Practices

1. **Run verification before every commit** that affects setup scripts
2. **Test on different environments** if possible (different OS, Python versions)
3. **Keep test scripts simple** and focused on core functionality
4. **Document any changes** to setup scripts in commit messages
5. **Use dry-run mode** for quick checks during development

## 🆘 Getting Help

If verification fails:

1. Check the error messages for specific issues
2. Run manual verification steps
3. Check the troubleshooting section in `scripts/README.md`
4. Ensure all prerequisites are met
5. Try running with verbose output for more details

## 📚 Related Documentation

- [Setup Scripts README](README.md) - Complete setup script documentation
- [Main Project README](../README.md) - Project overview and installation
- [Developer Documentation](../docs/developer/README.md) - Development setup

---

**Remember:** The goal is to ensure a smooth experience for users who clone your repository. Good setup scripts with proper verification make your project more professional and user-friendly! 
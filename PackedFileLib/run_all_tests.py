"""This triggers all the tests to make sure things work correctly."""

#Start a timer
import time

from tests.file_extract_test import file_extract_test
from tests.toc_load_test import load_toc_test

start_time = time.time()

test_file_path = "C:\\Games\\C2Recomp\\assets\\Wwise\\streaming.pack"

print("\nTriggering load test.")
if load_toc_test(test_file_path):
    print("\nLoad test completed successfully!")

print("\nTriggering file extraction test.")
if file_extract_test(test_file_path):
    print("\nFile extraction test completed successfully!")

print("ALL TESTS DONE! --- Tests took %s seconds total" % (time.time() - start_time))
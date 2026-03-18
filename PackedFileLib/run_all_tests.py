"""This triggers all the tests to make sure things work correctly."""

#Start a timer
import time

from tests.basic_toc_load_test import load_toc_test

start_time = time.time()

test_toc_file_path = "C:\\Games\\C2Recomp\\assets\\UI\\dropscreen.pack.toc"

print("\nTriggering load test.")
if load_toc_test(test_toc_file_path):
    print("\nLoad test completed successfully!")

print("ALL TESTS DONE! --- Tests took %s seconds total" % (time.time() - start_time))
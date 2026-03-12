import os
from robot.api import ExecutionResult, ResultVisitor

class FailureFinder(ResultVisitor):
    def __init__(self, target_test_name=None):
        self.failures = []
        self.target_test_name = target_test_name

    def visit_test(self, test):
        if test.status == 'FAIL':
            # If a target test name is specified, only capture that one.
            if self.target_test_name and test.name != self.target_test_name:
                return
            
            # Find the failing keyword
            failing_kw = self._find_failing_keyword(test)
            kw_name = failing_kw.name if failing_kw else "Unknown"
            kw_doc = failing_kw.doc if failing_kw else ""
            
            failure_info = {
                "test_name": test.name,
                "message": test.message,
                "failing_keyword": kw_name,
                "failing_keyword_doc": kw_doc,
                "tags": list(test.tags)
            }
            self.failures.append(failure_info)

    def _find_failing_keyword(self, item):
        # Recursively find the exact keyword that failed
        failing_kw = None
        if hasattr(item, 'body'):
            for step in item.body:
                if hasattr(step, 'status') and step.status == 'FAIL':
                    # It might be this step, or a child of this step
                    child_kw = self._find_failing_keyword(step)
                    if child_kw:
                        failing_kw = child_kw
                    else:
                        failing_kw = step
                    break
        return failing_kw

def parse_robot_output(xml_path: str, target_test_name: str = None) -> list:
    """
    Parses a Robot Framework output.xml file and extracts information 
    about failed tests, specifically the failing keyword and message.
    """
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"Output XML file not found at: {xml_path}")
        
    result = ExecutionResult(xml_path)
    finder = FailureFinder(target_test_name=target_test_name)
    result.visit(finder)
    
    return finder.failures

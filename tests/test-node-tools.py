#!/usr/bin/env python3

import argparse
import sys
import unittest

# The tools that have to be in the image, with the argument that makes them
# print their version.
TOOLS = {
    "node": "--version",
    "npm": "--version",
    "bower": "--version",
    "gulp": "--version",
    "jsdoc": "--version",
    "aws": "--version",
}


def run_tests(image_name, tools):
    import docker

    class TestNodeTools(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.client = docker.from_env()

        def run_command(self, command):
            container = self.client.containers.run(
                image_name, command=command, detach=True, stdout=True, stderr=True
            )
            result = container.wait()
            output = container.logs().decode("utf-8", errors="replace")
            container.remove()
            return result.get("StatusCode"), output

        def test_runs_as_unprivileged_user(self):
            print("Running the user test...")
            code, output = self.run_command(["id", "-u"])
            self.assertEqual(code, 0, f"The user could not be read: {output}")
            self.assertNotEqual(output.strip(), "0", "The container runs as root")
            print("User test passed.")

        def test_the_tools_are_there(self):
            print("Running the tools test...")
            for tool in tools:
                argument = TOOLS.get(tool, "--version")
                code, output = self.run_command([tool, argument])
                self.assertEqual(
                    code, 0, f"The tool {tool} is not in the image: {output}"
                )
            print("Tools test passed.")

        def test_the_entrypoint_runs_the_command(self):
            print("Running the entrypoint test...")
            code, output = self.run_command(["/bin/echo", "the entrypoint works"])
            self.assertEqual(code, 0, f"The command did not run: {output}")
            self.assertIn("the entrypoint works", output, f"The command did not run: {output}")
            print("Entrypoint test passed.")

    print(f"Checking the image '{image_name}'...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNodeTools)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the tests for the node images.")
    parser.add_argument(
        "--image",
        type=str,
        default="satishweb/node-bower-gulp:ci",
        help="The image that is tested",
    )
    parser.add_argument(
        "--tools",
        type=str,
        default="node,npm,bower,gulp",
        help="The tools that have to be in the image, separated by commas",
    )
    args = parser.parse_args()

    run_tests(args.image, [tool.strip() for tool in args.tools.split(",") if tool.strip()])

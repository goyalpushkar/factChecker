import sys
import os
import asyncio

# Add the project root to sys.path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
from source.services.lib.utils import Utils
from source.services.lib.Logger import Logger
from source.services.lib.readProperties import PropertiesReader

def test_utils_saveFile():
    """Test the saveFile method in Utils class."""
    try:
        logger = Logger().get_logger()
        utils = Utils(kwargs={"logger": logger})
        properties = PropertiesReader(kwargs={"logger":logger})

        captions_directory = properties.get_property("folders", "captions_directory")
        if not captions_directory:
            captions_directory = os.path.join(os.getcwd(), 'captionsDirectory')

        if not os.path.exists(captions_directory):
            os.makedirs(captions_directory)
        
        file_name = "test_file"
        text_to_save = "This is a test.\nLine 2 of the test file."
        
        result = utils.saveFile(captions_directory, file_name, text_to_save)
        
        assert result is True, "saveFile method failed to save the file."
        
        saved_file_path = os.path.join(captions_directory, f"{file_name}.txt")
        assert os.path.exists(saved_file_path), "Saved file does not exist."
        
        with open(saved_file_path, 'r') as file:
            content = file.read()
            assert content == text_to_save, "Content of the saved file does not match expected content."
        
        # Clean up
        os.remove(saved_file_path)
        # os.rmdir(captions_directory)
        
        print("test_utils_saveFile: All tests passed.")

        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Fact Checker Generic Testing")
    print("=" * 50)

    result = None
    try:
        result = test_utils_saveFile()

    except Exception as e:
        print(f"❌ An error occurred during the test setup: {e}")
    finally:
        print("\n📊 Test Results:")
        print(f"  Test File: {'✅ PASS' if result else '❌ FAIL'}")

        if result:
            print("\n🎉 All tests passed! System is ready to use.")
        else:
            print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())

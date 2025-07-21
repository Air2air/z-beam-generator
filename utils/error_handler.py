import logging
import traceback
import sys


class ErrorHandler:
    """Standardized error handling across the application."""
    
    @staticmethod
    def handle_component_error(component_name, error, strict_mode=True):
        """Handle an error in a component."""
        error_message = f"Error in {component_name}: {str(error)}"
        logging.error(error_message)
        
        if strict_mode:
            # In strict mode, re-raise the error
            raise RuntimeError(error_message)
        else:
            # In non-strict mode, return an error placeholder
            return f"<!-- {error_message} -->"
            
    @staticmethod
    def handle_api_error(provider, error):
        """Handle an API error."""
        error_message = f"API error with {provider}: {str(error)}"
        logging.error(error_message)
        
        # Always raise API errors to prevent using incomplete/incorrect content
        raise RuntimeError(error_message)
    
    @staticmethod
    def handle_application_error(location, error):
        """Handle an application-level error."""
        # Log the full stack trace
        logging.error(f"Application error in {location}: {str(error)}")
        logging.error(traceback.format_exc())
        
        # Print user-friendly message
        print(f"\n❌ Error in {location}: {str(error)}")
        print("Please check the log file for details.")
        
        # Return error code
        return 1
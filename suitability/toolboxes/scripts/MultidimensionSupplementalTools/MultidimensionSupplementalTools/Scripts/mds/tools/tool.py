# -*- coding: utf-8 -*-
import sys
if sys.platform == "win32":
    import ctypes


class Tool(object):

    @staticmethod
    def debug(
            value):
        """
        Show the string representation of *value* in a dialog box.
        """
        if sys.platform == "win32":
            ctypes.windll.user32.MessageBoxA(0, str(value), "Debug", 1)
        else:
            assert False, "TODO: Implement on {}".format(sys.platform)

    @staticmethod
    def parameter_must_be_initialized(
            parameter):
        """
        Return whether *parameter* must be initialized.

        The *parameter* passed in must be initialized if the user asks for it:

        * *parameter* is not altered and its value is None.
        """
        return (not parameter.altered) and (parameter.value is None)

    @staticmethod
    def parameter_is_new(
            parameter):
        """
        Return whether *parameter* is new.

        A parameter is new if it hasn't been validated yet.
        """
        assert parameter is not None
        return not parameter.hasBeenValidated

    @staticmethod
    def set_error(
            parameter,
            message):
        """
        Set an error *message* in the *parameter*, but only when no error
        has been set already. We don't want to overwrite an earlier set
        message.
        """
        if not parameter.hasError():
            parameter.setErrorMessage(message)

    @staticmethod
    def set_warning(
            parameter,
            message):
        """
        Set an warning *message* in the *parameter*, but only when no warning
        has been set already. We don't want to overwrite an earlier set
        message.
        """
        if not parameter.hasWarning():
            parameter.setWarningMessage(message)

    def __init__(self):
        pass


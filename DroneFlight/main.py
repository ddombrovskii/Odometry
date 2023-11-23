import subprocess
import os

if __name__ == '__main__':
    # Этот скрипт запускает все остальные в режиме тестирования
    this = os.path.basename(__file__)
    scripts = tuple(script for script in os.listdir('.') if script.endswith('.py') and script != this)
    for script in scripts:
        try:
            print(f"running script: \"{script}\"")
            with open(script) as script_code:
                exec(script_code.read())
            # subprocess.run(("python", script))
        except Exception | AttributeError | ValueError | KeyError | TypeError as ex:
            print(f"script: \"{script}\" cause following errors:\n{ex}")


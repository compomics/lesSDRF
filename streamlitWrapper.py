# import runpy
# runpy.run_module('streamlit.web.cli')
# import streamlit.web.cli
# import click
# click.pass_context
# if __name__ == '__main__':
#     streamlit.web.cli._main_run_clExplicit('Home.py', 'streamlit run')

import os
import sys
import streamlit.web.bootstrap

# sys.path.append('./')

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    flag_options = {
        "global.developmentMode": False,
    }

    streamlit.web.bootstrap.load_config_options(flag_options=flag_options)
    flag_options["_is_running_with_streamlit"] = True
    streamlit.web.bootstrap.run(
        "./application/Home.py",
        "streamlit run",
        [],
        flag_options,
    )
# import streamlit.web.cli as stcli
# import sys
# import os

# def resolve_path(path):
#     resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
#     print(os.getcwd())
#     print(path)
#     print(resolved_path)
#     return resolved_path

# def streamlit_run():
#      sys.argv=["streamlit", "run", "Home.py", "--global.developmentMode=false"]
#      sys.exit(stcli.main())

# if __name__ == "__main__":
#      streamlit_run()
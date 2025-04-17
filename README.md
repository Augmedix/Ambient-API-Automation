# Getting & Setting up the project

1. Clone the project at any location
2. Go to cloned project folder
3. Install all the dependencies by running the following command
      ```bash  
       pip install -r requirements.txt
      ```
4. Change the required environment specific info/data in the config files (**dev.properties**, **staging.properties** etc)



# Running the project

- **Running single testcase**
  
     ```bash
      pytest testsuiteFolder\subFolder1\...\subFolderN\test_module.py::Class_Name::test_method_name
     ```
     
- **Running testsuite/module**
  
     ```bash
      pytest testsuiteRootFolder\subFolder01\...\subFolderN\test_module.py
     ```
     
- **Running testcases in a folder**
  
     ```bash
      pytest your_test_folder_name
     ```

- **Running regression test**

  ```bash
  pytest
  ```

- **Running test parallelly in local machine**

  - Running tests parallelly module-wise/class-wise - 

    ```bash
    pytest -n number_of_worker_to_run --dist=loadscope
    ```
  
  - Running tests parallelly file-wise -
  
    ```bash
    pytest -n number_of_worker_to_run --dist=loadfile
    ```
  
    
# Custom *pyetest* flags

| Flag                  | Possible values                                              | *Default Flag Value*                                         | What are the flag values for?                                |
| :-------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **--env**             | **dev**/**development**, **stage**/**staging** **or** **prod**/**live**/**production** | Default value is set to ***dev*** if this flag is not used in the command. | If the **--env** is set to **staging** then system will start running using ***staging*** dataset provided in the **staging.properties** file values, if it is set to **production** then system will start running using **prduction.properties** file values. Otherwise, it will go with the **dev.properties** file's dataset. |
| **--url**             | **url** for either **dev**/**staging**/**live**              | No default value.                                            | If no **url** is explicitly provided in the CLI then it'll use the **url** provided in any of the properties files. If provided in the CLI, this value will override the value read from properties file. |
| **--browser**         | **chrome**<br />**firefox/ff**<br />**ie** - stands for **Internet Explorer**<br />**edge**<br />**hc/headless-chrome** | **chrome**                                                   | Used for browser selection.                                  |
| **--testrail-report** | **on** or **off**                                            | Default value is set to ***off*** if the flag is not used.   | When ***--testrail-result*** is set to ***on***, individual testcase result should be updated on ***TestRail*** after that specific testcase is executed. If it is set to ***off***, no status update will be reflected in ***TestRail***. |
| **--html**            | File name where reports/logs will be written.                | **N/A**                                                      | Used for generating an **HTML** report after completing test run. |
| **--testdox**         | **N/A**                                                      | **N/A**                                                      | Used for generating console report similar to **[mocha](https://pypi.org/project/pytest-testdox/)**. |
| **--mocha**           | **N/A**                                                      | **N/A**                                                      | Used for **[mocha](https://pypi.org/project/pytest-testdox/)** style reporting in console. |
| **-n**                | **auto** or **number of process** to run [values from 1 to any reasonable amount. | **N/A**                                                      | Flag **-n** used with value **auto** should run testcase with maximum numbers of **CPU** core available on your machine. Otherwise providing numeric value will also do. |
| **--dist=scope**      | **load**<br />**loadscope**<br />**loadfile**                | Default is **load**                                          | **load** - Sends pending tests to any worker that is available, without any guaranteed order.<br /> **loadscope** - tests are grouped by **module** for test functions and by **class** for test methods.<br />**loadfile** - Tests are grouped by their containing file. |
| **--no-skips**        | **True**/**False**                                           | Default is **False**.                                        | If provided with **True** value, all the skipped test cases will be forced to run. |
| **--enable-jenkins**  | **yes**/**no**                                               | Default is **no**.                                           | If provided **--enable-jenkins=yes** then it'll be run on grid from jenkins build. Otherwise it'll be run locally. |

**Note:** For simplicity, [**pytest** specific flags](https://docs.pytest.org/en/6.2.x/reference.html#command-line-flags) have been excluded from the list.

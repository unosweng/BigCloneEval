# **How to Set Up and Run find\_clone.py**

This guide provides step-by-step instructions for setting up the necessary environment and running the find\_clone.py Python script to query the BigCloneBench database.

## **Prerequisites**

Before you begin, ensure you have the following:

1. **The Complete BigCloneEval Project:** You must have the main BigCloneEval directory containing the bigclonebenchdb/, ijadataset/, and libs/ subdirectories.  
2. **Python 3:** The script is written for Python 3\.  
3. **An ARM-compatible JDK:** For modern Macs (Apple Silicon), you need a Java Development Kit (JDK) that matches your computer's AArch64 (ARM) architecture. We identified jdk-17.0.9-macos-aarch64 as a working version on your machine.

## **Setup Instructions**

### **Step 1: Install Python Dependencies**

The script requires the jaydebeapi library to connect to the Java-based H2 database. It's highly recommended to do this within a Python virtual environment.

1. **Navigate to your project directory:**  
   cd /Users/myoungkyu/Documents/0-git-repo/0-research-BigCloneEval/

2. **Create and activate a virtual environment (Recommended):**  
   python3 \-m venv myenv  
   source myenv/bin/activate

3. **Install the library:**  
   pip install jaydebeapi

### **Step 2: Place the Script**

Save the find\_clone.py script in a convenient location within your project. Based on your history, you have it in a src2 folder, which is perfectly fine.

* **Your script location:** /Users/myoungkyu/Documents/0-git-repo/0-research-BigCloneEval/src2/find\_clone.py

## **How to Run the Script**

You must run the script from the directory where it is located (src2 in your case) and provide the correct path to the project's root directory.

### **The Command Structure**

The command has three main parts:

1. **JAVA\_HOME=...**: Sets the correct Java environment to avoid architecture mismatch errors.  
2. **python find\_clone.py ...**: Executes the script.  
3. **\[IDs\] and \--path ..**: Provides the function ID(s) to query and the relative path to the project root.

### **Example Commands**

Execute these from the /.../BigCloneEval/src2/ directory.

1\. To Analyze a Specific Clone Pair (Two IDs):  
This command finds the clone relationship between functions 80378 and 18548122 and displays their source code.  
JAVA\_HOME=/Library/Java/JavaVirtualMachines/jdk-17.0.9-macos-aarch64/Contents/Home python find\_clone.py 80378 18548122 \--path ..

2\. To Get Details for a Single Function (One ID):  
This command finds all information and all clone partners for function 80378\.  
JAVA\_HOME=/Library/Java/JavaVirtualMachines/jdk-17.0.9-macos-aarch64/Contents/Home python find\_clone.py 80378 \--path ..

By following these steps, you can reliably run the script to explore any clone pair in the database.

## **Sample Output and Explanation**

Below is the full output from running the command to analyze the clone pair 80378 and 18548122\. Each section is explained.

Connecting to the database...  
Connection successful.

\--- Querying for details of Functions 80378 and 18548122 \---  
Function Details:  
NAME        TYPE       STARTLINE  ENDLINE    ID         NORMALIZED\_SIZE  PROJECT   TOKENS     INTERNAL  
\---------------------------------------------------------------------------------------------------------  
6607.java   default    32         75         80378      44               pgportal  392        False  
840452.java selected   42         52         18548122   11               gb-fwk    83         False

\=========================================================================================================

\--- Querying for specific Clone Pair between 80378 and 18548122 \---  
Found Clone Pair:  
FUNCTION\_ID\_ONE  FUNCTION\_ID\_TWO  FUNCTIONALITY\_ID  TYPE           SYNTACTIC\_TYPE  SIMILARITY\_LINE  SIMILARITY\_TOKEN   MIN\_SIZE ...  
\---------------------------------------------------------------------------------------------------------------------------------  
80378            18548122         2                 tagged-tagged  3               0.09090909...    0.19642857...      11       ...

\=================================================================================================================================

\--- Displaying Source Code \---  
\------------------------------------------------------------  
Displaying: 6607.java (Lines 32-75)  
\------------------------------------------------------------  
  32|     public static void test(String args\[\]) {  
  33|         int trace;  
... (code for function 1\) ...  
  75|     }  
\------------------------------------------------------------

\------------------------------------------------------------  
Displaying: 840452.java (Lines 42-52)  
\------------------------------------------------------------  
  42|     private static String loadUrlToString(String a\_url) throws IOException {  
  43|         URL l\_url1 \= new URL(a\_url);  
... (code for function 2\) ...  
  52|     }  
\------------------------------------------------------------

Database connection closed.

### **Explanation of Output Sections**

1. **Connection Messages:**  
   * Connecting to the database... and Connection successful. confirm that the script was able to find the H2 driver and connect to the bcb.h2.db file.  
2. **Function Details:**  
   * This section shows the data for each function, pulled from the FUNCTIONS table.  
   * **NAME:** The name of the source .java file.  
   * **TYPE:** The subdirectory within ijadataset/dataset/ where the file is located (default or selected).  
   * **STARTLINE / ENDLINE:** The line numbers defining the function's body within the source file.  
   * **ID:** The unique identifier for the function.  
   * **PROJECT:** The original source project of the function.  
3. **Found Clone Pair:**  
   * This section displays the row from the CLONES table that links the two functions.  
   * **FUNCTIONALITY\_ID:** A key piece of information. This number (2 in this case) tells you which subdirectory under ijadataset/bcb\_reduced/ contains the source files.  
   * **SYNTACTIC\_TYPE:** The type of clone (e.g., Type-3 is a syntactically dissimilar clone).  
   * **SIMILARITY\_LINE / SIMILARITY\_TOKEN:** Scores indicating how similar the two functions are, based on lines of code and code tokens, respectively. Lower numbers mean less similarity.  
4. **Displaying Source Code:**  
   * This is the final and most important part. The script uses the information from the previous steps to find the correct .java files and prints the exact lines of code for each function, allowing for a direct, side-by-side comparison.
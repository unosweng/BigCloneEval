# **How to Review Clones in BigCloneBench**

This guide provides a step-by-step process for connecting to the BigCloneBench H2 database, querying for a clone pair, and locating the corresponding source code files for manual review.

## **Objective**

To manually inspect a pair of code fragments (functions) that are identified as clones within the BigCloneBench dataset.

## **Prerequisites**

Before you begin, ensure you have completed the following setup steps from the BigCloneEval ReadMe.md:

1. **BigCloneEval Framework:** You have cloned the Git repository.  
2. **Matched Database and Dataset:** You have downloaded and extracted the correct, matched versions of the **BigCloneBench database** (into bigclonebenchdb/) and the **IJaDataset** (into ijadataset/).  
3. **Build Complete:** You have successfully run make from the project root to compile the Java source code.

### **Step 1: Connect to the Database**

The BigCloneEval project includes the specific version of the H2 database required to open the bcb.h2.db file. You must launch the console from this included file.

1. **Open your Terminal** and navigate to the root directory of your BigCloneEval project.  
2. **Start the H2 Console** by executing the .jar file located in the libs directory. The correct version is 1.3.176.  
   java \-jar libs/h2-1.3.176.jar

3. The H2 console will open in your web browser. On the login screen, enter the following **JDBC URL**. Make sure to replace \_PATH\_TO\_YOUR\_PROJECT\_ with the actual absolute path to your BigCloneEval folder.  
   jdbc:h2:file:/\_PATH\_TO\_YOUR\_PROJECT\_/BigCloneEval/bigclonebenchdb/BigCloneBench\_BCEvalVersion/bcb

   * **User Name:** sa  
   * **Password:** (leave blank)  
4. Click **Connect**.

### **Step 2: Find a Clone Pair**

The BCB\_CLONES table contains the definitions of all clone pairs, identified by the IDs of the two functions involved.

1. In the H2 console's SQL editor, run the following query to find a single Type-3 clone pair.  
   SELECT \* FROM BCB\_CLONES  
   WHERE SYNTACTIC\_TYPE \= 3  
   LIMIT 1;

2. From the results, note down the numbers in the **FUNCTION\_ID\_ONE** and **FUNCTION\_ID\_TWO** columns. These are the unique identifiers for the two functions in the clone pair.

### **Step 3: Get Function Details**

Now, use the two function IDs you found to retrieve the location details for each function from the FUNCTIONS table.

1. Replace ID\_1 and ID\_2 in the query below with the IDs you noted from Step 2\.  
   SELECT ID, NAME, STARTLINE, ENDLINE  
   FROM FUNCTIONS  
   WHERE ID \= ID\_1 OR ID \= ID\_2;

   For example:  
   SELECT ID, NAME, STARTLINE, ENDLINE  
   FROM FUNCTIONS  
   WHERE ID \= 1436629 OR ID \= 1285706;

2. This query will return two rows, one for each function. The key columns are:  
   * **ID**: The function's unique ID. This is also its filename.  
   * **NAME**: A string that tells you the subdirectory path. For example, java.selected.11.  
   * **STARTLINE / ENDLINE**: The location of the function within the file.

### **Step 4: Locate and View the Source Code**

The full path to a source file is constructed by combining information from the ID and NAME columns.

1. **Construct the Path**:  
   * Take the NAME column, e.g., java.selected.11.  
   * This translates to the path: ijadataset/bcb\_reduced/11/selected/.  
   * Take the ID column, e.g., 1285706\.  
   * This becomes the filename: 1285706.java.  
2. Combine them to get the full path from your project's root directory:  
   ijadataset/bcb\_reduced/11/selected/1285706.java  
3. **View the File**: Go back to your terminal (in the BigCloneEval root directory) and use a command like cat or less to view the contents of the file.  
   cat ijadataset/bcb\_reduced/11/selected/1285706.java

4. Repeat this process for the second function in the pair. You can now open both files and compare the code between the STARTLINE and ENDLINE to review the clone.
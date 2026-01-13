Start Antigravity, Open a Terminal und Start Gemini cli. You then will be given the option to install the Antigravity IDE Extension. Install it. After that you can install the usual Extension like context7/conductor. Then with /settings you can set it up as you Like. You can Authenticate with your Google subscription. You dont have the task Option but something better: everytime you send a prompt the Cli Reads your Gemini.md here you can say what it has to do, Like a system prompt. For example you can say it should always read X.md before responding etc. 

These issues should be addressed one by one. Please ask for any clarifications you may need. 

1 - The upload files button on the Hopper display should be removed. We only want users to be able to upload files to specific folders. That gives the app a clue as to what type, or source, of data will be processed. No files can therefore be uploaded until all the sun-folders in the hopper folder are created.


2 - While processing files succesfully, the status under "Processing Your Archive" says "failed (0%)" but the process is proceeding. The status icon is not being kept current with all of the phases or steps of processing. It may be helpful to add a "step" indicator to the status bar to show the current phase of processing. Since we know the count of how many emails have been extracted, we can show a percentage of the processing per step or phase of the processing. 

3 - You are using wrong the model names. The use of "gemini-1.5-flash" has been deprecated and is not to be used. 
Hence the error "Gemini Extraction Failed: 404 NOT_FOUND. {'error': {'code': 404, 'message': 'models/gemini-1.5-flash is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.', 'status': 'NOT_FOUND'}}" that is generated for all the processed emails. Use "gemini-2.5-pro" as the default model. Please review  the file "documents/gemini_model_management_spec.md" to see how the model name is to be managed. Please ask any questions you may have. 

4 - Selecting a .html file in the google drive folder should open it in the browser, instead it shows the content of the file. An example of this is the file "53b7ed6828bd9736d7044f7c92d823cf442c1934-20269272-111369791_google_com.html" which was produced by the last test run of the app. 
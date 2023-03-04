Summarize top N HackerNews using OpenAI API and convert the summary into audios using text-to-speech api.

### Prerequisite

- An OpenAI API account is required
- An Azure account is required

### Usage

Run the following command to generate the audio file.  The result will write
to an output.wav file.
```
AZURE_KEY=${YOUR_AZURE_KEY} \\
AZURE_REGION=${YOUR_AZURE_REGION} \\
OPENAI_ORG_ID=${YOUR_OPENAI_ORG_ID} \\
OPENAI_API_TOKEN=${YOUR_OPENAI_TOKEN} \\
python main.py
```

### Limitations

- Cannot access webpage content if there is paywall or pop ups
- Summary may not make sense if 
  - The content is a github page
  - The content is heavy on non-textual information, e.g. code scripts
  - The content is a list page instead of detail page
- Some long text may cause too many requests to OpenAI
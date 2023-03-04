Summarize top N HackerNews using OpenAI API and convert the summary into audios using text-to-speech api.

### Prerequisite

- An OpenAI API account is required
- An Azure account is required

### Setup Environment

```
# Install python dependencies
pip install -r requirements.txt
```

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

### Bypass Paywalls
Follow the following steps if your source articles have paywalls and you decide to bypass them.

1. Download the [iamadamdev/bypass-paywalls-chrome](https://github.com/iamadamdev/bypass-paywalls-chrome) 
Chrome extension.
2. Install playwright browser and let it know where to look for the bypass-paywalls-chrome extension.
```
playwright install chrome
export BYPASS_PAYWALL_DIR=${PATH_TO_BYPASS_PAYWALLS_CHROM_EXTENSION}
```
3. Let the program know that you need to bypass paywalls by setting the following environment variable
```
export BYPASS_PAYWALL=True
```

### Limitations

- Cannot access webpage content if there is paywall or pop ups
- Summary may not make sense if 
  - The content is a github page
  - The content is heavy on non-textual information, e.g. code scripts
  - The content is a list page instead of detail page
- Some long text may cause too many requests to OpenAI
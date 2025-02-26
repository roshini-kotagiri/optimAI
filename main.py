import fitz
import google.generativeai as genai
import csv

#configure with your api before starting..
genai.configure(api_key='')

def extract_text_from_pdf(fileName):
    print('Extracting Text...')
    try:
        doc = fitz.open(fileName)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def summary_text(text, col_name):

    print('Summarizing...')
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    Extract the following structured information from the text:
    
    A concise summary (max 2-3 sentences) covering the main points.
    Mentioned the below features with there extracted ones from input text, if not then just put N/A
    Features : {col_name}
    
    Important Instructions:
    Do NOT include any special characters or extra formatting.
    Summary field shouldn't be empty or N/A 
    
    Input Text:
    {text}
    
    Restricted Response Format:
    Summary: <Extracted Summary>
    <followed by feature:<Extracted Feature>>
    Give just above response don't add any out of it
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"API error: {e}")
        if "safety" in str(e).lower() or "harm" in str(e).lower():
            print("Content may have triggered safety filters. Try with less text or different content.")
        return None

def save_to_csv_file(response):
    print('Saving...')
    if not response:
        print("No response to save")
        return
        
    try:
        response_arr = response.splitlines()
        csv_row = []
        for line in response_arr:
            if ":" in line:
                value = line.split(":", 1)[1].strip()
                csv_row.append(value)
            else:
                csv_row.append(line)
                
        with open('sample.csv', mode='a',newline='')as file:
            writer = csv.writer(file)
            writer.writerow(csv_row)
        print('Saved Successfully')
    except Exception as e:
        print(f"CSV save error: {e}")

def extract_col_names_from_csv(csv_fileName):
    print('Extracting Column Names...')
    with open(csv_fileName,'r',newline='') as file:
        csv_reader = csv.reader(file)
        try:
            return next(csv_reader)
        except StopIteration:
            return []

def main():
    fileName = input('Enter File Path: ')
    csv_fileName = input('Enter CSV File Path: ')
    try:
        text = extract_text_from_pdf(fileName)
        col_name = extract_col_names_from_csv(csv_fileName)
        if text:
            response = summary_text(text,col_name)
            if response:
                print(response)
                save_to_csv_file(response)
            else:
                print("Failed to get summary from API")
        else:
            print("Failed to extract text from PDF")
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    main()
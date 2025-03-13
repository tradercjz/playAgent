
from llm_client import LLMClient, LLMResponse
from dotenv import load_dotenv
from file_manager import FileManager
import html2text
from prompt import PromptTemplates
import os
import threading

# 配置和初始化
load_dotenv()

from concurrent.futures import ThreadPoolExecutor, as_completed

def process_function(func):
    """Process a single function documentation."""
    if os.path.exists(f"./cleandocs/{func}.txt"):
        print(f"doc for {func} is already cleaned, skip")
        return
    
    doc = FileManager.find_function_html_file("./docs", func)
    if doc is None:
        print(f"func {func} is None")
        return
    
    try:
        llm_client = LLMClient()
        with open(doc, "r", encoding='utf-8') as f:
            content = f.read()
            origin_text = html2text.html2text(content)
            llm_result = llm_client.generate_response([
                {
                    "role": "system",
                    "content": PromptTemplates.html_doc_clean()
                },
                {
                    "role": "user",
                    "content": origin_text
                }
            ])

            if llm_result.success:
                with open(f"./cleandocs/{func}.txt", "w") as wf:
                    wf.write(llm_result.content)
                print(f"Successfully processed {func}")
            else:
                print(f"Failed to process {func}: LLM request unsuccessful")
    except Exception as e:
        print(f"Error processing {func}: {str(e)}")

def main():
    functions = [
        "matrix"
        # "bondAccrInt", "bondConvexity", "bondDirtyPrice", "bondDuration", "nss", 
        # "ns", "condValueAtRisk", "nsspredict", "trueRange", "valueAtRisk",
        # "irs", "varma", "bondCashflow", "bondYield", "createPricingEngine", 
        # "treasuryConversionFactor", "crmwCBond", "cds", "vanillaOption", 
        # "maxDrawdown", "mdd", "cummdd", "createYieldCurveEngine", "appendForPrediction"
    ]
    
    os.makedirs("./cleandocs", exist_ok=True)
    
    max_workers = 5
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_func = {executor.submit(process_function, func): func for func in functions}
        
        for future in as_completed(future_to_func):
            func = future_to_func[future]
            try:
                future.result() 
            except Exception as exc:
                print(f"{func} generated an exception: {exc}")

if __name__ == "__main__":
    main()



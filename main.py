from stock_analysis.chains import (
    CompanyOverviewChain, ReferencesChain, FundamentalAnalysisChain,
    CallTranscriptChain, PressReleaseChain, QnATranscriptsCallChain,
    TechnicalAnalysisChain, AnalystCoverageChain, NotableFactsChain
)
import pdfkit
import markdown2
from yfinance import Ticker
from markdown_pdf import MarkdownPdf, Section
from markdown_it import MarkdownIt
import datetime
import io

# Configuration for wkhtmltopdf
today = datetime.date.today()
PATH_WKHTMLTOPDF = 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'  # Adjust as needed
CONFIG = pdfkit.configuration(wkhtmltopdf=PATH_WKHTMLTOPDF)

def get_user_inputs():
    """Collect and validate user inputs."""
    while True:
        try:
            ticker = input("Input ticker: ").strip().upper()
            year = today.year + 1
            quarter = 4
            etf = input("ETF/Mutual fund? Yes or No: ").strip().lower()
            if not etf:
                raise ValueError("Yes or No")
            etf = etf == "yes"
            info = Ticker(ticker=ticker).info
            if info == {'trailingPegRatio': None} or quarter not in (1, 2, 3, 4):
                raise ValueError("Invalid ticker or quarter.")
        except Exception as e:
            print(f"Invalid input, please try again. ({e})")
        else:
            return ticker, year, quarter, etf


def generate_section(chain_class, *args, **kwargs) -> str:
    try:
        print(f"Generating content for {chain_class.__name__}")
#         return f"""
# TEST  ++++++++++++++++++++++++

# ## {chain_class.__name__}

# The **earnings call transcript** for **Apple Inc. (AAPL)**, Q4 2024, highlighted key points about the company's performance and strategic directions:

# 1. **Revenue Highlights**:
#    - Total revenue for the quarter reached $100 billion, driven by strong sales in the iPhone and Mac product lines.
#    - Emerging markets contributed significantly, with India and Brazil showing record growth rates.

# 2. **Guidance for Future Quarters**:
#    - The management projected revenue growth of 8-10% for the next fiscal year.
#    - Increased investment in research and development, particularly in AI and wearable technologies.

# 3. **Key Management Commentary**:
#    - CEO Tim Cook emphasized Apple's focus on sustainability, with plans to transition to fully renewable energy in all facilities by 2026.
#    - CFO Luca Maestri discussed improvements in supply chain efficiencies and robust demand for services like iCloud and Apple Music.

# 4. **Q&A Highlights**:
#    - **Question**: "How is Apple addressing inflationary pressures on product pricing?"
#      **Answer**: "We are committed to offering value through innovation and operational efficiency, ensuring minimal impact on our customers."
#    - **Question**: "What is Apple's strategy for the AR/VR market?"
#      **Answer**: "We are investing heavily in this space and anticipate significant contributions from the Vision Pro headset in the coming years."

# This summary offers a detailed snapshot of the discussion during the earnings call and management's forward-looking perspectives.
# TEST +++++++++++++++++++++++++++++++++++++++
# """
        chain = chain_class(*args, **kwargs)
        output = chain.execute_chain()
        if output == "":
            raise Exception()
        else:
            print(f"Output for {chain_class.__name__} generated successfully")  # Print first 100 chars
            return output
    except Exception as e:
        print(f"Error generating content for {chain_class.__name__} {e}")
        return ""


def build_sections(ticker, year, quarter, etf, test=False):
    """Generate all report sections based on the input parameters."""
    overview_section = generate_section(CompanyOverviewChain, ticker)
    fundamental_section = generate_section(FundamentalAnalysisChain, ticker)
    technical_section = generate_section(TechnicalAnalysisChain, ticker)
    if not etf:
        PressRelease_section = generate_section(PressReleaseChain, ticker=ticker, q=quarter, year=year)
        CallTranscript_section = generate_section(CallTranscriptChain, ticker=ticker, q=quarter, year=year)
        QnATranscriptsCall_section = generate_section(QnATranscriptsCallChain, ticker=ticker, q=quarter, year=year)
        analysts_section = generate_section(AnalystCoverageChain, ticker=ticker)
    notable_section = generate_section(NotableFactsChain, ticker)
    references_section = generate_section(ReferencesChain, ticker, etf=etf)

    # Conditional sections for non-ETF cases
    if etf:
        sections = {
            "Overview": overview_section,
            "Fundamental Analysis": fundamental_section,  # Fixed key
            "Holdings and Sector Allocation": "skip",
            "Technical Analysis": technical_section,
            "Facts to Know about {}".format(ticker): notable_section,
            "Analyst Recommendations": "skip",
            "Research Articles": references_section,
            "References": "skip",  # Placeholder for references section
        }
    else:
        sections = {
            "Overview": overview_section,
            "Fundamental Analysis": fundamental_section,  # Fixed key
            "Technical Analysis": technical_section,
            "Press Release Summary": PressRelease_section,
            "Call Transcripts": CallTranscript_section,  # Fixed key
            "Q&A": QnATranscriptsCall_section,
            "Analyst Recommendations": analysts_section,
            "Facts to Know about {}".format(ticker): notable_section,
            "Research Articles": references_section,
            "References": "skip",  # Placeholder for references section
        }
    return sections

def create_toc(sections):
    """Generate a Markdown table of contents with subpoints for nested sections."""
    toc = "# Table of Contents\n"
    counter = 1
    done = False

    for section, content in sections.items():
        # Only add to TOC if content exists
        if content:
            if section == "Press Release Summary" and not done:
                # Main section number
                toc += f"{counter}. [Earning Report](#earning-report)\n"
                # Check if the sub-sections have content before adding them
                if sections.get("Press Release Summary"):
                    toc += f"   1. [Press Release Summary](#press-release-summary)\n"
                if sections.get("Q&A"):
                    toc += f"   2. [Q&A](#q&a-responses)\n"
                counter += 1
                done = True
            elif section and section not in ["Q&A", "Press Release Summary", "Call Transcripts"]:
                # Regular sections
                toc += f"{counter}. [{section}](#{section.lower().replace(' ', '-')})\n"
                counter += 1

    return toc


def convert_to_html(markdown_content, info={}, ticker="TEST"):
    """Convert Markdown content to styled HTML."""
    html_content = markdown2.markdown(markdown_content)
    styled_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            div.report-title {{
                    font-family: 'Helvetica', sans-serif;
                    color: #000000;            
                    font-size: 32px;
                    text-align: center;
                }}
            body {{
                font-family: 'Arial', sans-serif;
                font-size: 22px;
                line-height: 1.7;
                color: #333;
            }}
            h1, h2, h3 {{
                color: #003366;
            }}
            h1 {{ font-size: 29px; }}
            h2 {{ font-size: 24px; }}
            h3 {{ font-size: 20px; }}
            
            p, li {{
                font-size: 16px;
            }}

            table, tr, td, thead, th, tbody, ul, ol, li, pre, blockquote, img, div, p{{
                page-break-inside: avoid;
            }}

            /* Enforce page breaks before headers */
            
        </style>
    </head>
    <body>
        <div class="report-title">Comprehensive Investment Report on {info.get("longName", "TEST")} ({ticker})</div>
        {html_content}
    </body>
    </html>
    """
    return styled_html


def generate_pdf(html_content, ticker):
    """Generate a PDF from HTML content."""
    options = {
        "page-size": "A4",
        "margin-top": "1in",
        "margin-right": "0.8in",
        "margin-bottom": "1in",
        "margin-left": "0.8in",
        "encoding": "UTF-8",
        "header-html": "./header.html",
    }
    pdfkit.from_string(html_content, f"./data/{ticker}_report.pdf", options=options, configuration=CONFIG)

def generate_pdf_with_markdown(markdown_content,info, ticker):
    user_css = f"""
    body {{
            font-family: 'Arial', sans-serif;
            font-size: 16px;
            line-height: 1.5;
            color: #333;
        }}
    h1, h2, h3 {{
        color: #003366;
    }}
    h1 {{ font-size: 20px; }}
    h2 {{ font-size: 16px; }}
    h3 {{ font-size: 12px; }}

    p, li {{
        font-size: 10px;
    }}
    """
    pdf = MarkdownPdf(toc_level=2)
    pdf.meta["title"] = 'Title'
    pdf.add_section(Section(markdown_content, toc=True), user_css=user_css)
    pdf.save(f'./data/{ticker}_report.pdf')
    with open("test_output.md", "w", encoding="utf-8") as error_file:
            error_file.write(markdown_content)

# GENERATE WITH MARKDOWN_IT
def generate_pdf_with_markdown_it(markdown_content):
    md = MarkdownIt()
    output = md.render(src=markdown_content)
    output = convert_to_html(output)
    with open("markdown_it.html", "w", encoding="utf-8") as error_file:
            error_file.write(output)


def main(test=False, use_wkhtmltopdf=True, use_markdown_it=False):
    """Main function to orchestrate the report generation."""
    if test:
        markdown_content = open("test.md", "r").read()
        info={}
        ticker = "TEST_wkhtmltopdf = " + str(use_wkhtmltopdf)
    else:
        ticker, year, quarter, etf = get_user_inputs()
        # ticker, year, quarter, etf= "AAPL", 2024, 4, False
        info = Ticker(ticker=ticker).info
        
        
        sections = build_sections(ticker, year, quarter, etf)

        toc = create_toc(sections)
        # print(toc)
        print()
        print(markdown2.markdown(toc))
        markdown_content = toc + "\n\n"
        for title, content in sections.items():
        # Ensure content exists
            if content and not content == "skip":
                if title == "Press Release Summary":
                    markdown_content += f"\n# Earning Report\n\n## {title}\n\n{content}\n"
                elif title == "Q&A":
                    markdown_content += f"\n## {title}\n\n{content}\n"
                elif title in ("Call Transcripts", "Fundamental Analysis"):
                    markdown_content += f"\n{content}\n"  # Add only content without title
                else:
                    markdown_content += f"\n# {title}\n\n{content}\n"  # Add title and content for other sections
    markdown_content = markdown_content.replace("\n## ", "\n### ")
    # saving Markdown output for debugging purposes
    with open("md_out.md", "w", encoding="utf-8") as md_out:
        md_out.write(markdown_content)
                    
    try:
        if use_markdown_it:
            generate_pdf_with_markdown_it(markdown_content)
        elif not use_wkhtmltopdf:
            # print("Wtih markdown")
            generate_pdf_with_markdown(markdown_content,info, ticker)
        else:
            html_content = convert_to_html(markdown_content, info, ticker=ticker)
            # Saving the HTML for debugging purposes
            with open("html_out.html", "w", encoding="utf-8") as html_out:
                html_out.write(html_content)

            generate_pdf(html_content, ticker)
 
        # print(f"PDF for {ticker} generated successfully!")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        with open("error_output.md", "w", encoding="utf-8") as error_file:
            error_file.write(markdown_content)

if __name__ == "__main__":
    main(test=False, use_wkhtmltopdf=True, use_markdown_it=False)
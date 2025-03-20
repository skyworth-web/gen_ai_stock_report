import markdown2

test = """### 10. [GSK Sees Strong Demand For Vaccines and Asthma Drugs, Raises Annual Outlook](https://finance.yahoo.com/news/gsk-sees-strong-demand-vaccines-154217851.html)
   **Summary**: GSK anticipates strong demand for vaccines and asthma drugs, leading to an increased annual outlook 
with expected EPS growth of 8% to 10% in 2024.

## References:
1. [https://finance.yahoo.com/quote/GSK/news/](https://finance.yahoo.com/quote/GSK/news/)
2. [https://www.gsk.com/en-gb/media/press-releases/gsk-delivers-strong-2022-performance-with-full-year-sales-of-293-billion/](https://www.gsk.com/en-gb/media/press-releases/gsk-delivers-strong-2022-performance-with-full-year-sales-of-293-billion/)
3. [https://www.gsk.com/en-gb/media/press-releases/gsk-delivers-strong-2023-performance-and-upgrades-growth-outlooks/](https://www.gsk.com/en-gb/media/press-releases/gsk-delivers-strong-2023-performance-and-upgrades-growth-outlooks/)
4. [https://www.wsj.com/business/earnings/gsk-lifts-guidance-after-higher-turnover-beats-market-views-f0043426](https://www.wsj.com/business/earnings/gsk-lifts-guidance-after-higher-turnover-beats-market-views-f0043426)
5. [https://www.nasdaq.com/articles/gsks-new-drugs-and-pipeline-hold-the-key-to-growth-in-2023](https://www.nasdaq.com/articles/gsks-new-drugs-and-pipeline-hold-the-key-to-growth-in-2023)
6. [https://finance.yahoo.com/news/gsk-outperforms-industry-strength-key-154400643.html](https://finance.yahoo.com/news/gsk-outperforms-industry-strength-key-154400643.html)
7. [https://us.gsk.com/en-us/media/press-releases/new-gsk-to-deliver-step-change-in-growth-and-performance-over-nextover-next-ten-years/)
8. [https://www.pharmalive.com/gsk-2023-strategic-transformation-unfolds/](https://www.pharmalive.com/gsk-2023-strategic-transformation-unfolds/)
9. [https://www.gsk.com/en-gb/media/press-releases/gsk-makes-a-strong-start-to-2024-with-improving-outlook-for-the-year/](https://www.gsk.com/en-gb/media/press-releases/gsk-makes-a-strong-start-to-2024-with-improving-outlook-for-the-year/)
10. [https://finance.yahoo.com/news/gsk-sees-strong-demand-vaccines-154217851.html](https://finance.yahoo.com/news/gsk-sees-strong-demand-vaccines-154217851.html)
   """

print(test)
print(markdown2.markdown(test))
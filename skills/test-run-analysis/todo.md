Improve the recommendations when empty to point to creating evaluation skills, UI or documentation. Example of poor result:
 
 Recommendations

  1. Configure Evaluations: Set up evaluation criteria for this prompt to measure quality in future test runs. Consider adding:
    - Auto evaluations (LLM-as-judge for criteria like accuracy, relevance, format compliance)
    - Expected outputs for test cases to enable automated scoring
  2. Review Test Case Outputs: Manually review the 5 test case outputs in the Freeplay UI to assess prompt performance
  3. Rerun with Evaluations: Once evaluations are configured, rerun the test to get quantitative metrics
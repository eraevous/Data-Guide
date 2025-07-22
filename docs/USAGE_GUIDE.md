# Usage Guide

This guide outlines common workflows for generating Data Guides.

1. **Prepare input data**
   - Place CSV files in a directory (default `input/`).
   - Adjust custom type hints in `src/data_pipeline/config.py` if needed.

2. **Run the pipeline**
   ```bash
   python src/pipeline.py <input_dir> <output_dir>
   ```
   Reports and plots are written to the specified output directory.

3. **Custom Profiling**
   - Run the Typer CLI with a config file:
   ```bash
   python src/profiler_cli.py profile --config my_config.json --output-dir reports
   ```
   - You can also use `DataProfiler` directly for single DataFrames and call `generate_report()`.

See the template in `templates/data_guide_template.md` for report structure.

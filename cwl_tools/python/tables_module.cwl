cwlVersion: v1.0

class: CommandLineTool

requirements:
- class: InlineJavascriptRequirement
- class: ResourceRequirement
  ramMin: 4000
  coresMin: 1

baseCommand: tables_module

inputs:

  standard_waltz_metrics_pool_a:
    type: Directory
    inputBinding:
      prefix: --standard_waltz_pool_a

  unfiltered_waltz_metrics_pool_a:
    type: Directory
    inputBinding:
      prefix: --unfiltered_waltz_pool_a

  simplex_waltz_metrics_pool_a:
    type: Directory
    inputBinding:
      prefix: --simplex_waltz_pool_a

  duplex_waltz_metrics_pool_a:
    type: Directory
    inputBinding:
      prefix: --duplex_waltz_pool_a

  standard_waltz_metrics_pool_b:
    type: Directory
    inputBinding:
      prefix: --standard_waltz_pool_b

  unfiltered_waltz_metrics_pool_b:
    type: Directory
    inputBinding:
      prefix: --unfiltered_waltz_pool_b

  simplex_waltz_metrics_pool_b:
    type: Directory
    inputBinding:
      prefix: --simplex_waltz_pool_b

  duplex_waltz_metrics_pool_b:
    type: Directory
    inputBinding:
      prefix: --duplex_waltz_pool_b


  standard_waltz_metrics_pool_a_exon_level:
    type: Directory
    inputBinding:
      prefix: --standard_waltz_metrics_pool_a_exon_level

  unfiltered_waltz_metrics_pool_a_exon_level:
    type: Directory
    inputBinding:
      prefix: --unfiltered_waltz_metrics_pool_a_exon_level

  simplex_waltz_metrics_pool_a_exon_level:
    type: Directory
    inputBinding:
      prefix: --simplex_waltz_metrics_pool_a_exon_level

  duplex_waltz_metrics_pool_a_exon_level:
    type: Directory
    inputBinding:
      prefix: --duplex_waltz_metrics_pool_a_exon_level

outputs:

  tables:
    type: Directory
    outputBinding:
      glob: '.'
      outputEval: |
        ${
          self[0].basename = 'aggregate_tables';
          return self[0]
        }

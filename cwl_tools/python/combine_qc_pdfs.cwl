cwlVersion: v1.0

class: CommandLineTool

baseCommand: [combine_qc_pdfs]

inputs:

  project_name:
    type: string
    inputBinding:
      prefix: -p

  title_page:
    type: File
    inputBinding:
      position: 1

  read_counts:
    type: File
    inputBinding:
      position: 2

  average_coverage_exon_level_A:
    type: File
    inputBinding:
      position: 3

  align_rate:
    type: File
    inputBinding:
      position: 4

  on_target_rate:
    type: File
    inputBinding:
      position: 5

  gc_cov_each_sample:
    type: File
    inputBinding:
      position: 6

  insert_sizes:
    type: File
    inputBinding:
      position: 7

  coverage_per_interval:
    type: File
    inputBinding:
      position: 8

  cov_and_family_type_A:
    type: File
    inputBinding:
      position: 9

  cov_and_family_type_B:
    type: File
    inputBinding:
      position: 10

  base_quality_plot:
    type: File
    inputBinding:
      position: 11

  family_sizes_simplex:
    type: File
    inputBinding:
      position: 12

  family_sizes_duplex:
    type: File
    inputBinding:
      position: 13

  noise_alt_percent:
    type: File
    inputBinding:
      position: 14

  noise_by_substitution:
    type: File
    inputBinding:
      position: 15

  noise_contributing_sites:
    type: File
    inputBinding:
      position: 16

  hotspots_in_normals_plot:
    type: File
    inputBinding:
      position: 17

  hotspots_in_normals_table_pdf:
    type: File
    inputBinding:
      position: 18

  fingerprinting_qc:
    type: File
    inputBinding:
      position: 19

  gender_check:
    type: File
    inputBinding:
      position: 20

  pipeline_inputs:
    type: File
    inputBinding:
      position: 21

outputs:

  combined_qc:
    type: File
    outputBinding:
      glob: '*.pdf'

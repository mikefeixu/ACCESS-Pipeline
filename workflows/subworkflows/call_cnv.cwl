cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}

inputs:

  tumor_sample_list: File
  normal_sample_list: File
  targets_coverage_bed: File
  targets_coverage_annotation: File

  reference_fasta: File
  project_name: string
  threads: int

outputs:
#check this with example output JIRA
    tumors_covg:
        type: File
        outputSource: coverage/tumors_covg
    normals_covg:
        type: File
        outputSource: coverage/normals_covg
    bam_list:
        type: File[]
        outputSource: coverage/bam_list

    tumor_loess_text:
        type: File
        outputSource: loess_tumor/loess_text
    normal_loess_text:
        type: File
        outputSource: loess_normal/loess_text
    tumor_loess_pdf:
        type: File
        outputSource: loess_tumor/loess_pdf
    normal_loess_pdf:
        type: File
        outputSource: loess_normal/loess_pdf

    genes_file:
        type: File
        outputSource: copy_number/genes_file
    probes_file:
        type: File
        outputSource: copy_number/probes_file
    intragenic_file:
        type: File
        outputSource: copy_number/intragenic_file
    copy_pdf:
        type: File
        outputSource: copy_number/copy_pdf
    seg_files:
        type: File[]
        outputSource: copy_number/seg_files

steps:

  coverage:
    run: ../../cwl_tools/cnv/coverage.cwl
    in:
      project_name_cnv: project_name
      threads: threads
      tumor_sample_list: tumor_sample_list
      normal_sample_list: normal_sample_list
      targets_coverage_bed: targets_coverage_bed
      reference_fasta: reference_fasta

    out: [tumors_covg, normals_covg, bam_list]


  loess_tumor:
    run: ../../cwl_tools/cnv/loess.cwl
    in:
      project_name_cnv: project_name
      coverage_file: coverage/tumors_covg
      run_type:
        default: tumor
      targets_coverage_annotation: targets_coverage_annotation

    out: [loess_text, loess_pdf]


  loess_normal:
    run: ../../cwl_tools/cnv/loess.cwl
    in:
      project_name_cnv: project_name
      coverage_file: coverage/normals_covg
      run_type:
        default: normal
      targets_coverage_annotation: targets_coverage_annotation

    out: [loess_text, loess_pdf]


  copy_number:
    run: ../../cwl_tools/cnv/copynumber.cwl
    in:
      project_name_cnv: project_name
      loess_normals: loess_normal/loess_text
      loess_tumors: loess_tumor/loess_text
      do_full:
        default: MIN
      targets_coverage_annotation: targets_coverage_annotation

    out: [genes_file, probes_file, copy_pdf, intragenic_file, seg_files]

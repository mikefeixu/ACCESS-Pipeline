cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/run_tools/schemas.yaml

inputs:

  # Todo: what to do with these?
  project_name: string
  version: string

  sample_id: string[]

  tumor_bams:
    type: File[]
    secondaryFiles: [^.bai]

  normal_bams:
    type: File[]
    secondaryFiles: [^.bai]

  reference_fasta:
    type: File
    secondaryFiles: [.fai]

  run_tools: ../../resources/run_tools/schemas.yaml#sv_run_tools

outputs:

  sv_directory:
    type: Directory[]
    outputSource: manta/sv_directory

  annotated_sv_file:
    type: File[]
    outputSource: annotate_manta/sv_file_annotated

steps:

  filter_tumor_reads_ending_in_indels:
    run: ../../cwl_tools/manta/manta_filter.cwl
    in:
      bam: tumor_bams
      output_file_name:
        valueFrom: $(inputs.bam.basename.replace('.bam', '_term-indel-filt.bam'))
    out: [filtered_bam]
    scatter: [bam]
    scatterMethod: dotproduct

  filter_normal_reads_ending_in_indels:
    run: ../../cwl_tools/manta/manta_filter.cwl
    in:
      bam: normal_bams
      output_file_name:
        valueFrom: $(inputs.bam.basename.replace('.bam', '_term-indel-filt.bam'))
    out: [filtered_bam]
    scatter: [bam]
    scatterMethod: dotproduct

  index_tumor:
    run: ../../cwl_tools/samtools/index.cwl
    in:
      bam: filter_tumor_reads_ending_in_indels/filtered_bam
    out: [indexed_bam]
    scatter: [bam]
    scatterMethod: dotproduct

  index_normal:
    run: ../../cwl_tools/samtools/index.cwl
    in:
      bam: filter_normal_reads_ending_in_indels/filtered_bam
    out: [indexed_bam]
    scatter: [bam]
    scatterMethod: dotproduct

  manta:
    run: ../../cwl_tools/manta/manta.cwl
    in:
      run_tools: run_tools
      r_path:
        valueFrom: $(inputs.run_tools.r_path)
      sv_repo:
        valueFrom: $(inputs.run_tools.sv_repo)
      manta:
        valueFrom: $(inputs.run_tools.manta)

      sample_id: sample_id
      tumor_sample: index_tumor/indexed_bam
      normal_sample: index_normal/indexed_bam

      reference_fasta: reference_fasta
    scatter: [sample_id, tumor_sample, normal_sample]
    scatterMethod: dotproduct
    out: [sv_vcf, sv_directory]

  annotate_manta:
    run: ../../cwl_tools/manta/manta_annotation.cwl
    in:
      run_tools: run_tools
      sv_repo:
        valueFrom: $(inputs.run_tools.sv_repo)
      manta:
        valueFrom: $(inputs.run_tools.manta)

      vcf: manta/sv_vcf
      sample_id: sample_id

      output_dir:
        valueFrom: $('.')
      reference_fasta: reference_fasta
    scatter: [vcf, sample_id]
    scatterMethod: dotproduct
    out: [sv_file_annotated]

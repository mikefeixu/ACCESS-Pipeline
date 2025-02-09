cwlVersion: v1.0

class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  ScatterFeatureRequirement: {}
  SubworkflowFeatureRequirement: {}
  StepInputExpressionRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/collapsing_tools.yaml
      - $import: ../../resources/schemas/params/print_reads.yaml
      - $import: ../../resources/schemas/params/base_recalibrator.yaml

inputs:
  run_tools: ../../resources/schemas/collapsing_tools.yaml#run_tools

  print_reads__params: ../../resources/schemas/params/print_reads.yaml#print_reads__params
  base_recalibrator__params: ../../resources/schemas/params/base_recalibrator.yaml#base_recalibrator__params

  bams:
    type: File[]
    secondaryFiles:
      - ^.bai

  reference_fasta: string

  bqsr__knownSites_dbSNP:
    type: File
    secondaryFiles: [.idx]

  bqsr__knownSites_millis:
    type: File
    secondaryFiles: [.idx]

outputs:

  bqsr_bams:
    type: File[]
    secondaryFiles:
      - ^.bai
    outputSource: parallel_printreads/bams

  recalibrated_scores_matrix:
    type: File[]
    outputSource: parallel_bqsr/recal_matrix

steps:

  parallel_bqsr:
    in:
      run_tools: run_tools
      params: base_recalibrator__params
      java:
        valueFrom: ${return inputs.run_tools.java_7}
      gatk:
        valueFrom: ${return inputs.run_tools.gatk_path}
      bam: bams
      reference_fasta: reference_fasta
      rf:
        valueFrom: $(inputs.params.rf)
      nct:
        valueFrom: $(inputs.params.nct)

      known_sites_1: bqsr__knownSites_dbSNP
      known_sites_2: bqsr__knownSites_millis
    out: [recal_matrix]
    scatter: bam
    scatterMethod: dotproduct

    run:
      class: Workflow
      inputs:
        java: string
        gatk: string
        bam:
          type: File
          secondaryFiles: [^.bai]
        reference_fasta: string
        rf: string
        nct: int
        known_sites_1: File
        known_sites_2: File
      outputs:
        recal_matrix:
          type: File
          outputSource: bqsr/recal_matrix
      steps:
        bqsr:
          run: ../../cwl_tools/gatk/BaseQualityScoreRecalibration.cwl
          in:
            java: java
            gatk: gatk
            input_bam: bam
            reference_fasta: reference_fasta
            rf: rf
            nct: nct
            known_sites_1: known_sites_1
            known_sites_2: known_sites_2
            out:
              valueFrom: $(inputs.input_bam.basename.replace('.bam', '.recal_matrix'))
          out: [recal_matrix]

  parallel_printreads:
    in:
      run_tools: run_tools
      params: print_reads__params
      java:
        valueFrom: ${return inputs.run_tools.java_7}
      gatk:
        valueFrom: ${return inputs.run_tools.gatk_path}

      input_file: bams
      BQSR: parallel_bqsr/recal_matrix

      nct:
        valueFrom: $(inputs.params.nct)
      EOQ:
        valueFrom: $(inputs.params.EOQ)
      baq:
        valueFrom: $(inputs.params.baq)

      reference_sequence: reference_fasta
    out: [bams]
    scatter: [input_file, BQSR]
    scatterMethod: dotproduct

    run:
      class: Workflow
      inputs:
        java: string
        gatk: string
        input_file: File
        BQSR: File
        nct: int
        EOQ: boolean
        reference_sequence: string
        baq: string
      outputs:
        bams:
          type: File
          secondaryFiles:
            - ^.bai
          outputSource: gatk_print_reads/out_bams
      steps:
        gatk_print_reads:
          run: ../../cwl_tools/gatk/PrintReads.cwl
          in:
            java: java
            gatk: gatk
            input_file: input_file
            BQSR: BQSR
            nct: nct
            EOQ: EOQ
            baq: baq
            reference_sequence: reference_sequence
            out:
              valueFrom: ${return inputs.input_file.basename.replace(".bam", "_BR.bam")}
          out: [out_bams]

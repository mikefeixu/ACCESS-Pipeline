cwlVersion: v1.0

class: Workflow

requirements:
  StepInputExpressionRequirement: {}
  InlineJavascriptRequirement: {}
  SchemaDefRequirement:
    types:
      - $import: ../../resources/schemas/variants_tools.yaml
      - $import: ../../resources/schemas/params/bcftools.yaml

inputs:

  run_tools: ../../resources/schemas/variants_tools.yaml#run_tools
  bcftools_params: ../../resources/schemas/params/bcftools.yaml#bcftools_params

  vcf_vardict:
    type: File
    secondaryFiles: [.tbi]
  vcf_mutect:
    type: File
    secondaryFiles: [.tbi]

  tumor_sample_name: string
  normal_sample_name: string
  annotate_concat_input_header: File

outputs:

  combined_vcf:
    type: File
    outputSource: concat/concat_vcf_output_file

  annotated_combined_vcf:
    type: File
    outputSource: annotate_concat/annotated_concat_vcf_output_file

steps:

  create_vcf_file_array:
    in:
      vcf_vardict: vcf_vardict
      vcf_mutect: vcf_mutect
    out: [vcf_files]
    run:
      class: ExpressionTool
      requirements:
        - class: InlineJavascriptRequirement

      inputs:
        vcf_vardict:
          type: File
          secondaryFiles:
            - .tbi

        vcf_mutect:
          type: File
          secondaryFiles:
            - .tbi

      outputs:
        vcf_files:
          type: File[]
          secondaryFiles:
            - .tbi

      expression: "${
        var project_object = {};
        project_object['vcf_files'] = [inputs.vcf_vardict, inputs.vcf_mutect];
        return project_object;
      }"

  concat:
    run: ../../cwl_tools/bcftools/bcftools_concat.cwl
    in:
      run_tools: run_tools
      bcftools:
        valueFrom: $(inputs.run_tools.bcftools)
      bcftools_params: bcftools_params
      vcf_files: create_vcf_file_array/vcf_files
      tumor_sample_name: tumor_sample_name
      normal_sample_name: normal_sample_name
      allow_overlaps:
        valueFrom: $(inputs.bcftools_params.allow_overlaps)
      rm_dups:
        valueFrom: $(inputs.bcftools_params.rm_dups)
      output:
        valueFrom: $(inputs.tumor_sample_name + '.' + inputs.normal_sample_name + '.combined-variants.vcf')
    out: [concat_vcf_output_file]

  annotate_concat:
    run: ../../cwl_tools/concatVCF/annotate_concat.cwl
    in:
      combined_vcf: concat/concat_vcf_output_file
      anno_with_vcf: vcf_mutect
      anno_header: annotate_concat_input_header
    out: [annotated_concat_vcf_output_file]

cwlVersion: v1.0

class: CommandLineTool

requirements:
  ResourceRequirement:
    ramMin: 16000

arguments:
#- Rscript
- /opt/common/CentOS_6-dev/R/R-3.5.0/bin/Rscript
- $(inputs.sv_repo.path + '/scripts/manta_sample.R')

inputs:

  sv_repo: Directory

  tumor_sample:
    type: File
    secondaryFiles: [^.bai]
    inputBinding:
      prefix: --tumor

  normal_sample:
    type: File
    secondaryFiles: [^.bai]
    inputBinding:
      prefix: --normal

  output_directory:
    type: string
    default: .
    inputBinding:
      prefix: --output

  reference_fasta:
    type: File
    secondaryFiles: [.fai]
    inputBinding:
      prefix: --fasta

  manta:
    type: Directory
    inputBinding:
      prefix: --manta

outputs:

  sv_vcf:
    type: File
    outputBinding:
      glob: 'results/variants/somaticSV.vcf.gz'

  sv_directory:
    type: Directory
    outputBinding:
      glob: '.'

import os
import sys
from setuptools import setup, find_packages
from subprocess import check_output
from python_tools._version import get_and_write_version


def req_file(filename):
    """
    We're using a requirements.txt file so that pyup.io can use this for security checks

    :param filename:
    :return str:
    """
    with open(filename) as f:
        content = f.readlines()
        content = filter(lambda x: not x.startswith("#"), content)
    return [x.strip() for x in content]


def get_package_files(directory, file_type):
    """
    helper function to recursively extract specific file types from the repository.

    :param directory, file_type:
    :return str:
    """
    paths = []
    for (path, directories, filenames) in os.walk(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), directory)
    ):
        for filename in filenames:
            if not filename.endswith(file_type):
                continue
            paths.append(os.path.join("..", path, filename))
    return paths


ENTRY_POINTS = """
        [console_scripts]
        create_access_project = python_tools.pipeline_kickoff.create_access_project:main
        create_inputs_from_title_file = python_tools.pipeline_kickoff.create_inputs_from_title_file:main
        create_standard_bam_to_collapsed_qc_inputs = python_tools.pipeline_kickoff.create_standard_bam_to_collapsed_qc_inputs:main
        create_title_file_from_manifest = python_tools.pipeline_kickoff.create_title_file_from_manifest:main
        create_title_file_from_samplesheet = python_tools.pipeline_kickoff.create_title_file_from_samplesheet:main
        create_title_file_from_samplesheet_legacy = python_tools.pipeline_kickoff.create_title_file_from_samplesheet_legacy:main
        pipeline_submit = python_tools.pipeline_kickoff.pipeline_submit:main
        pipeline_runner = python_tools.pipeline_kickoff.pipeline_runner:main
        list2bed = python_tools.workflow_tools.list2bed:main
        print_hotspots_in_normals_table_pdf = cwl_tools.bioinfo_utils.print_hotspots_in_normals_table_pdf:main
        qc_wrapper = python_tools.workflow_tools.qc.qc_wrapper:main
        tables_module = python_tools.workflow_tools.qc.tables_module:main
        base_quality_plot = python_tools.workflow_tools.qc.base_quality_plot:main
        plot_noise = python_tools.workflow_tools.qc.plot_noise:main
        fingerprinting = python_tools.workflow_tools.qc.fingerprinting:main
        combine_qc_pdfs = python_tools.workflow_tools.qc.combine_qc_pdfs:main
        gender_check = python_tools.workflow_tools.qc.gender_check:main
        pipeline_postprocessing = python_tools.workflow_tools.pipeline_postprocessing:main
        workflow_runtime_stats = python_tools.workflow_tools.workflow_runtime_stats:main
        test_outputs = python_tools.test.test_pipeline_outputs:main
        generate_access_variants_inputs = python_tools.pipeline_kickoff.generate_access_variants_inputs:main
        generate_access_variants_inputs_cmo = python_tools.pipeline_kickoff.generate_access_variants_inputs_cmo:main
        generate_copynumber_inputs = python_tools.pipeline_kickoff.generate_copynumber_inputs:main
        generate_msi_inputs = python_tools.pipeline_kickoff.generate_msi_inputs:main
        filter_mutect = cwl_tools.basicfiltering.filter_mutect:main
        filter_vardict = cwl_tools.basicfiltering.filter_vardict:main
        tag_hotspots = cwl_tools.hotspots.tag_hotspots:main
        ACCESS_filters = python_tools.workflow_tools.ACCESS_filters:main
        remove_variants_by_annotation = cwl_tools.remove_variants_by_anno.remove_variants_by_annotation:main
        annotate_concat = cwl_tools.concatVCF.annotate_concat:main
        maf2tsv = python_tools.workflow_tools.maf2tsv:main
        traceback_inputs = cwl_tools.traceback.traceback_inputs:main
        traceback_integrate = cwl_tools.traceback.traceback_integrate:main
        cfdna_scna = cwl_tools.cnv.scripts.cfdna_scna:main
        admie_analyze = cwl_tools.msi.scripts.admie_analyze:main
        """

SUPPORT_SCRIPTS = [
    "cwl_tools/bioinfo_utils/plot_hotspots_in_normals.r",
    "python_tools/workflow_tools/qc/r_tools/plots_module.r",
    "cwl_tools/bioinfo_utils/plot_hotspots_in_normals.r",
    "python_tools/workflow_tools/qc/r_tools/plots.r",
    "python_tools/workflow_tools/qc/r_tools/util.r",
    "python_tools/workflow_tools/qc/r_tools/constants.r",
    "python_tools/workflow_tools/qc/calculate_noise.sh",
    "python_tools/workflow_tools/qc/make_umi_qc_tables.sh",
    "python_tools/workflow_tools/qc/aggregate_bam_metrics.sh",
    "cwl_tools/cnv/scripts/copynumber_tm.batchdiff_cfdna.R",
    "cwl_tools/cnv/scripts/loessnormalize_nomapq_cfdna.R",
]


setup(
    name="access_pipeline",
    version=get_and_write_version(),
    description="MSKCC Center for Molecular Oncology, Innovation Lab, cfDNA sequencing pipeline",
    url="http://github.com/mskcc/ACCESS-Pipeline",
    author="Ian Johnson, Gowtham Jayakumaran",
    author_email="johnsoni@mskcc.org",
    license="MIT",
    install_requires=req_file("requirements.txt"),
    python_requires=">=2.7",
    classifiers=[
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 2.7",
    ],
    packages=find_packages(exclude=["test"]),
    package_data={
        "resources": get_package_files("resources", (".cwl", ".yaml")),
        "cwl_tools": get_package_files("cwl_tools", (".py", ".R")),
    },
    include_package_data=True,
    entry_points=ENTRY_POINTS,
    scripts=SUPPORT_SCRIPTS,
    zip_safe=False,
)

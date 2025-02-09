#!/usr/bin/env python

import os
import sys
import argparse
import pandas as pd

from python_tools.util import extract_sample_id_from_bam_path


def make_traceback_map(genotyping_bams, title_file, traceback_bam_inputs):
    """
    create a df with all required values for traceback function
    """

    def bam_type(bam):
        """
        helper function to derive bam type from the basename of bam file
        """
        if "simplex" in os.path.basename(bam):
            return "SIMPLEX"
        elif "duplex" in os.path.basename(bam):
            return "DUPLEX"
        else:
            return "STANDARD"

    title_file_df = pd.read_csv(title_file, sep="\t", header="infer", dtype=str)
    # get project name
    project_name = title_file_df["Pool"].unique().values.tolist().pop()
    # get unique sample IDs
    tumor_sample_ids = title_file_df["Sample"].values.tolist()
    # get unique patient IDs
    patient_ids = title_file_df["Patient_ID"].values.tolist()

    bam_paths = []
    bam_types = []
    bam_sample_ids = []
    bam_patient_ids = []
    for bam in genotyping_bams:
        bam_sample_id = extract_sample_id_from_bam_path(bam)
        if bam_sample_id in tumor_sample_ids:
            bam_paths.append(bam)
            bam_types.append(bam_type(bam))
            bam_sample_ids.append(bam_sample_id)
            bam_patient_ids.append(
                dict(zip(tumor_sample_ids, patient_ids))[bam_sample_id]
            )
    project_name_list = [project_name] * len(bam_paths)

    traceback_bam = pd.read_csv(
        traceback_bam_inputs, header="infer", sep="\t", dtype=str
    )
    bam_paths.extend(traceback_bam["BAM_file_path"].values.tolist())
    bam_patient_ids.extend(traceback_bam["MRN"].values.tolist())
    bam_sample_ids.extend(traceback_bam["Sample"].values.tolist())
    project_name_list.extend(traceback_bam["Run"].values.tolist())
    bam_types.extend(["STANDARD"] * int(traceback_bam.shape[0]))

    genotyping_ids = [
        "_".join([bam, bamtype])
        for bam, bamtype in dict(zip(bam_sample_ids, bam_types)).iteritems()
    ]

    traceback_map = pd.DataFrame(
        data={
            "Project": project_name_list,
            "Sample": bam_sample_ids,
            "Patient_ID": bam_patient_ids,  # this is the common id for
            "Genotyping_ID": genotyping_ids,
            "BAM": bam_paths,
        }
    )
    return traceback_map


def group_mutations_maf(title_file, TI_mutations, exonic_filtered, silent_filtered):
    """
    Main function that groups all mutations from the current project and 
    from applicable prior projects and returns a uniformly formatted
    maf file which can be used as a input file for genotyping
    """

    def _vcf_to_maf_coord(Start, Ref, Alt):
        """
        transform ref,alt,pos to maf format following vcf2maf rules
        """
        maf_start, maf_ref, maf_alt = int(Start), Ref, Alt
        ref_length, alt_length = len(Ref), len(Alt)
        while all([maf_ref, maf_alt, maf_ref[0] == maf_alt[0], maf_ref != maf_alt]):
            maf_ref = maf_ref[1:] or "-"
            maf_alt = maf_alt[1:] or "-"
            ref_length -= 1
            alt_length -= 1
            maf_start += 1

        # Handle SNPs, DNPs, TNPs, or anything larger (ONP)
        if ref_length == alt_length:
            return (
                str(maf_start),
                str(maf_start + alt_length - 1),
                maf_ref,
                maf_alt,
                _variant_type(maf_ref, maf_alt),
            )
        # Handle complex and non-complex deletions
        elif ref_length > alt_length:
            return (
                str(maf_start),
                str(maf_start + ref_length - 1),
                maf_ref,
                maf_alt,
                "DEL",
            )
        # Handle complex and non-complex insertions
        else:
            maf_stop = (
                str(maf_start + ref_length - 1) if maf_ref != "-" else str(maf_start)
            )
            maf_start = str(maf_start - 1) if maf_ref == "-" else str(maf_start)
            return (maf_start, maf_stop, maf_ref, maf_alt, "INS")

    def _variant_type(Ref, Alt):
        """
        get variant type based on maf formatted ref and alt 
        """
        if len(Ref) > len(Alt):
            return "DEL"
        elif len(Ref) < len(Alt):
            return "INS"
        else:
            snv_types = {1: "SNP", 2: "DNP", 3: "TNP"}
            if len(Ref) > 3:
                return "ONP"
            else:
                return snv_types[len(Ref)]

    def _TI_mutations_to_maf(TI_mutations):
        """
        helper function to reformat mutations from applicable previous project
        to maf format
        """
        TI_df = pd.read_csv(TI_mutations, sep="\t", header="infer", dtype=str)

        TI_df[
            [
                "Start_Position",
                "End_Position",
                "Reference_Allele",
                "Tumor_Seq_Allele2",
                "Variant_Type",
            ]
        ] = pd.DataFrame(
            TI_df.apply(
                lambda x: _vcf_to_maf_coord(
                    x["Start_Pos"], x["Ref_Allele"], x["Alt_Allele"]
                ),
                axis=1,
            ).values.tolist()
        )
        TI_df["Tumor_Seq_Allele1"] = TI_df["Reference_Allele"]
        TI_df["T_AltCount"] = (
            TI_df["T_Count"].apply(int) - TI_df["T_RefCount"].apply(int)
        ).apply(int)
        for col in [
            "VariantClass",
            "Gene",
            "Normal_Sample_ID",
            "T_RefCount",  # SD_T_RefCount",
            "T_AltCount",  # SD_T_AltCount",
            "N_RefCount",
            "N_AltCount",
        ]:
            if col not in TI_df.columns:
                TI_df[col] = ""

        TI_df = TI_df[
            [
                "Gene",
                "Chromosome",
                "Start_Position",
                "End_Position",
                "Reference_Allele",
                "Tumor_Seq_Allele1",
                "Tumor_Seq_Allele2",
                "Sample",
                "Normal_Sample_ID",
                "T_RefCount",  # For prior ACCESS samples, this should reflect SD_T_RefCount
                "T_AltCount",  # For prior ACCESS samples, this should reflect SD_T_AltCount
                "N_RefCount",
                "N_AltCount",
                "VariantClass",
                "Start_Pos",
                "Ref_Allele",
                "Alt_Allele",
                "Run",
                "MRN",
                "Accession",
            ]
        ].rename(
            index=str,
            columns={
                "Gene": "Hugo_Symbol",
                "Chromosome": "Chromosome",
                "Start_Position": "Start_Position",
                "End_Position": "End_Position",
                "Reference_Allele": "Reference_Allele",
                "Tumor_Seq_Allele1": "Tumor_Seq_Allele1",
                "Tumor_Seq_Allele2": "Tumor_Seq_Allele2",
                "Sample": "Tumor_Sample_Barcode",
                "Normal_Sample_ID": "Matched_Norm_Sample_Barcode",
                # "SD_T_RefCount": "t_ref_count",
                # "SD_T_AltCount": "t_alt_count",
                "T_RefCount": "t_ref_count",
                "T_AltCount": "t_alt_count",
                "N_RefCount": "n_ref_count",
                "N_AltCount": "n_alt_count",
                "VariantClass": "Variant_Classification",
                "Start_Pos": "VCF_POS",
                "Ref_Allele": "VCF_REF",
                "Alt_Allele": "VCF_ALT",
                "Run": "Run",
                "Accession": "Accession",
                "MRN": "MRN",
            },
        )
        return TI_df

    title_file_df = pd.read_csv(title_file, sep="\t", header="infer", dtype=str)
    title_file_df = title_file_df[
        ["Pool", "Sample", "Patient_ID", "AccessionID", "Class"]
    ]
    print(title_file_df["Patient_ID"])
    # get the list of input mutation files from the current project
    mutation_file_list = [exonic_filtered, silent_filtered]
    # read each of the file into a df
    df_from_each_file = (
        pd.read_csv(f, index_col=None, header=0, sep="\t", dtype=str)
        for f in mutation_file_list
    )
    # convert all all variant to maf and concat into a single df
    concat_df = pd.concat(df_from_each_file, ignore_index=True)
    concat_df[
        [
            "Start_Position",
            "End_Position",
            "Reference_Allele",
            "Tumor_Seq_Allele2",
            "Variant_Type",
        ]
    ] = pd.DataFrame(
        concat_df.apply(
            lambda x: _vcf_to_maf_coord(x["Start"], x["Ref"], x["Alt"]), axis=1
        ).values.tolist()
    )

    concat_df["Tumor_Seq_Allele1"] = concat_df["Reference_Allele"]

    concat_df = pd.merge(
        concat_df, title_file_df, how="left", left_on=["Sample"], right_on=["Sample"]
    )
    # remove
    concat_df = concat_df[~concat_df["Class"].str.contains("Pool")][
        [
            "Gene",
            "Chrom",
            "Start_Position",
            "End_Position",
            "Reference_Allele",
            "Tumor_Seq_Allele1",
            "Tumor_Seq_Allele2",
            "Sample",
            "NormalUsed",
            "SD_T_RefCount",
            "SD_T_AltCount",
            "N_RefCount",
            "N_AltCount",
            "VariantClass",
            "Start",
            "Ref",
            "Alt",
            "Pool",
            "Patient_ID",
            "AccessionID",
        ]
    ]
    concat_df = concat_df.rename(
        index=str,
        columns={
            "Gene": "Hugo_Symbol",
            "Chrom": "Chromosome",
            "Start_Position": "Start_Position",
            "End_Position": "End_Position",
            "Reference_Allele": "Reference_Allele",
            "Tumor_Seq_Allele1": "Tumor_Seq_Allele1",
            "Tumor_Seq_Allele2": "Tumor_Seq_Allele2",
            "Sample": "Tumor_Sample_Barcode",
            "NormalUsed": "Matched_Norm_Sample_Barcode",
            "SD_T_RefCount": "t_ref_count",
            "SD_T_AltCount": "t_alt_count",
            # "T_RefCount": "t_ref_count",
            # "T_AltCount": "t_alt_count",
            "N_RefCount": "n_ref_count",
            "N_AltCount": "n_alt_count",
            "VariantClass": "Variant_Classification",
            "Start": "VCF_POS",
            "Ref": "VCF_REF",
            "Alt": "VCF_ALT",
            "Pool": "Run",
            "AccessionID": "Accession",
            "Patient_ID": "MRN",
        },
    )

    # if mutations from previous project provided, format them and add
    #  them to the df as well
    if TI_mutations:
        concat_df = pd.concat(
            [concat_df, _TI_mutations_to_maf(TI_mutations)], sort=False
        )
    concat_df.to_csv(
        "traceback_inputs.maf", header=True, index=None, sep="\t", mode="w"
    )
    return


def main():
    """
    Parse arguments

    :return:
    """
    parser = argparse.ArgumentParser(
        prog="traceback_inputs.py", description="FILL", usage="%(prog)s [options]"
    )
    parser.add_argument(
        "-t",
        "--title_file",
        action="store",
        dest="title_file",
        required=False,
        help="Title file",
    )
    parser.add_argument(
        "-tm",
        "--ti_mutations",
        action="store",
        dest="ti_mutations",
        required=False,
        help="Input txt file of tumor informed mutations",
    )
    parser.add_argument(
        "-ef",
        "--exonic_filtered",
        action="store",
        dest="exonic_filtered",
        required=True,
        help="Path to exonic filtered mutations file",
    )
    parser.add_argument(
        "-sf",
        "--silent_filtered",
        action="store",
        dest="silent_filtered",
        required=True,
        help="Path to silent filtered mutations file",
    )

    args = parser.parse_args()
    group_mutations_maf(
        args.title_file, args.ti_mutations, args.exonic_filtered, args.silent_filtered
    )
    # TODO:
    # make a traceback map so that duplex and simplex bam mutations can be supported.
    #  currently, only standard/IMPACT bam mutations are supported.
    # make_traceback_map(
    #    args.tumor_duplex_bams + args.tumor_simplex_bams,
    #    args.title_file,
    #    traceback_bam_inputs,
    # )


if __name__ == "__main__":
    main()


#     maf_df = pd.read_csv(maf, header="infer", sep="\t", skiprows=1)
#     mad_df = maf_df[MAF_HEADER]

#     for mut_file in mutations_file_list:

#     title_file_df = pd.read_csv(title_file, header="infer", sep="\t")
#     mutations = pd.read_csv(mutation_list, header="infer", sep="\t")
#     bams = pd.read_csv(bam_list, header="infer", sep="\t")
#     unique_samples = list(
#         set(
#             title_file_df["MRN"].values.tolist(),
#             mutations["MRN"].values.tolist(),
#             bams["MRN"].values.tolist(),
#         )
#     )
#     for samples in unique_samples:
#         make_vcf


# def variants_to_vcf(group, project_name, variant_file):
#     vcf_list = []
#     variants = pd.read_csv(variant_file, header="infer")
#     variants = variants["Sample", "MRN", "Chrom", "Start", "Ref", "Alt"]
#     for sample in variants["Sample"].values.tolist().unique():
#         with open(sample + "_traceback_input.vcf", "w") as f:
#             f.write(TRACEBACK_INPUT_VCF_HEADER + "\n")
#         sample_vcf = variants[variants["Sample"] == sample]
#         sample_vcf.to_csv(
#             sample + "_traceback_input.vcf",
#             header=False,
#             index=None,
#             sep="\t",
#             mode="a",
#         )
#         vcf_list.append(sample + "_traceback_input.vcf")
#     return vcf_list

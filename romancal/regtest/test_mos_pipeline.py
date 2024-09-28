""" Roman tests for the High Level Pipeline """

import os

import pytest
import roman_datamodels as rdm

from romancal.pipeline.mosaic_pipeline import MosaicPipeline

from .regtestdata import compare_asdf


@pytest.mark.bigdata
@pytest.mark.soctests
@pytest.fixture(scope="module")
def run_mos(rtdata_module):
    rtdata = rtdata_module
    rtdata.get_asn("WFI/image/L3_regtest_asn.json")

    # Test Pipeline
    output = "r0099101001001001001_F158_visit_i2d.asdf"
    rtdata.output = output
    args = [
        "roman_mos",
        rtdata.input,
    ]
    MosaicPipeline.from_cmdline(args)
    rtdata.get_truth(f"truth/WFI/image/{output}")
    return rtdata


@pytest.fixture(scope="module")
def output_filename(run_mos):
    return run_mos.output


@pytest.fixture(scope="module")
def output_model(output_filename):
    with rdm.open(output_filename) as model:
        yield model


@pytest.fixture(scope="module")
def truth_filename(run_mos):
    return run_mos.truth


@pytest.fixture(scope="module")
def thumbnail_filename(output_filename):
    thumbnail_filename = output_filename.rsplit("_", 1)[0] + "_thumb.png"
    preview_cmd = f"stpreview to {output_filename} {thumbnail_filename} 256 256 roman"
    os.system(preview_cmd)  # nosec
    return thumbnail_filename


@pytest.fixture(scope="module")
def preview_filename(output_filename):
    preview_filename = output_filename.rsplit("_", 1)[0] + "_preview.png"
    preview_cmd = f"stpreview to {output_filename} {preview_filename} 1080 1080 roman"
    os.system(preview_cmd)  # nosec
    return preview_filename


def test_output_matches_truth(output_filename, truth_filename, ignore_asdf_paths):
    # DMS356
    diff = compare_asdf(output_filename, truth_filename, **ignore_asdf_paths)
    assert diff.identical, diff.report()


def test_thumbnail_exists(thumbnail_filename):
    # DMS356
    # FIXME was not an assert before
    assert os.path.isfile(thumbnail_filename)


def test_preview_exists(preview_filename):
    # DMS356
    # FIXME was not an assert before
    assert os.path.isfile(preview_filename)


@pytest.mark.parametrize("suffix", ("cat", "segm"))
def test_file_exists(output_filename, suffix):
    # DMS374 for catalog and segm
    # FIXME was not an assert before
    expected_filename = output_filename.rstrip("_", 1)[0] + f"_{suffix}.asdf"
    assert os.path.isfile(expected_filename)


def test_output_is_mosaic(output_model):
    # DMS356
    # FIXME comment says result is an ImageModel... it's not
    assert isinstance(output_model, rdm.datamodels.MosaicModel)


@pytest.mark.parametrize(
    "step_name",
    (
        "skymatch",
        "outlier_detection",
        "resample",
    ),
)
def test_steps_ran(output_model, step_name):
    # DMS356
    # DMS400 for skymatch
    # DMS86 for outlier_detection and resample
    assert getattr(output_model.meta.cal_step, step_name) == "COMPLETE"


def test_added_background(output_model):
    # DMS400
    assert hasattr(output_model.meta.individual_image_meta, "background")


def test_added_background_level(output_model):
    # DMS400
    assert any(output_model.meta.individual_image_meta.background["level"] != 0)

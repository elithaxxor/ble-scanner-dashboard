def test_lookup_vendor(tmp_path):
    data = tmp_path / "vendors.csv"
    data.write_text("001122,TestVendor\n")
    from vendor_lookup import VENDOR_CACHE, load_vendor_data, lookup_vendor
    VENDOR_CACHE.clear()
    load_vendor_data(data)
    assert lookup_vendor("00:11:22:33:44:55") == "TestVendor"

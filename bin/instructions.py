#!/usr/bin/env python
""" AMD Southern Islands instruction helper functions """

SOP2 = [
    's_add_u32',
    's_sub_u32',
    's_add_i32',
    's_sub_i32',
    's_addc_u32',
    's_subb_u32',
    's_min_i32',
    's_min_u32',
    's_max_i32',
    's_max_u32',
    's_cselect_b32',
    's_cselect_b64',
    's_and_b32',
    's_and_b64',
    's_or_b32',
    's_or_b64',
    's_xor_b32',
    's_xor_b64',
    's_andn2_b32',
    's_andn2_b64',
    's_orn2_b32',
    's_orn2_b64',
    's_nand_b32',
    's_nand_b64',
    's_nor_b32',
    's_nor_b64',
    's_xnor_b32',
    's_xnor_b64',
    's_lshl_b32',
    's_lshl_b64',
    's_lshr_b32',
    's_lshr_b64',
    's_ashr_i32',
    's_ashr_i64',
    's_bfm_b32',
    's_bfm_b64',
    's_mul_i32',
    's_bfe_u32',
    's_bfe_i32',
    's_bfe_u64',
    's_bfe_i64',
    's_cbranch_g_fork',
    's_absdiff_i32',
]

SOPK = [
    's_movk_i32',
    's_cmovk_i32',
    's_cmpk_eq_i32',
    's_cmpk_lg_i32',
    's_cmpk_gt_i32',
    's_cmpk_ge_i32',
    's_cmpk_lt_i32',
    's_cmpk_le_i32',
    's_cmpk_eq_u32',
    's_cmpk_lg_u32',
    's_cmpk_gt_u32',
    's_cmpk_ge_u32',
    's_cmpk_lt_u32',
    's_cmpk_le_u32',
    's_addk_i32',
    's_mulk_i32',
    's_cbranch_i_fork',
    's_getreg_b32',
    's_setreg_b32',
    's_setreg_imm32_b32',
]

SOP1 = [
    's_mov_b32',
    's_mov_b64',
    's_cmov_b32',
    's_cmov_b64',
    's_not_b32',
    's_not_b64',
    's_wqm_b32',
    's_wqm_b64',
    's_brev_b32',
    's_brev_b64',
    's_bcnt0_i32_b32',
    's_bcnt0_i32_b64',
    's_bcnt1_i32_b32',
    's_bcnt1_i32_b64',
    's_ff0_i32_b32',
    's_ff0_i32_b64',
    's_ff1_i32_b32',
    's_ff1_i32_b64',
    's_flbit_i32_b32',
    's_flbit_i32_b64',
    's_flbit_i32',
    's_flbit_i32_i64',
    's_sext_i32_i8',
    's_sext_i32_i16',
    's_bitset0_b32',
    's_bitset0_b64',
    's_bitset1_b32',
    's_bitset1_b64',
    's_getpc_b64',
    's_setpc_b64',
    's_swappc_b64',
    's_rfe_b64',
    's_and_saveexec_b64',
    's_or_saveexec_b64',
    's_xor_saveexec_b64',
    's_andn2_saveexec_b64',
    's_orn2_saveexec_b64',
    's_nand_saveexec_b64',
    's_nor_saveexec_b64',
    's_xnor_saveexec_b64',
    's_quadmask_b32',
    's_quadmask_b64',
    's_movrels_b32',
    's_movrels_b64',
    's_movreld_b32',
    's_movreld_b64',
    's_cbranch_join',
    's_abs_i32',
    's_mov_fed_b32',
]

SOPC = [
    's_cmp_eq_i32',
    's_cmp_lg_i32',
    's_cmp_gt_i32',
    's_cmp_ge_i32',
    's_cmp_lt_i32',
    's_cmp_le_i32',
    's_cmp_eq_u32',
    's_cmp_lg_u32',
    's_cmp_gt_u32',
    's_cmp_ge_u32',
    's_cmp_lt_u32',
    's_cmp_le_u32',
    's_bitcmp0_b32',
    's_bitcmp1_b32',
    's_bitcmp0_b64',
    's_bitcmp1_b64',
    's_setvskip',
]

SOPP = [
    's_nop',
    's_endpgm',
    's_branch',
    's_cbranch_scc0',
    's_cbranch_scc1',
    's_cbranch_vccz',
    's_cbranch_vccnz',
    's_cbranch_execz',
    's_cbranch_execnz',
    's_barrier',
    's_waitcnt',
    's_sethalt',
    's_sleep',
    's_setprio',
    's_sendmsg',
    's_sendmsghalt',
    's_trap',
    's_icache_inv',
    's_incperflevel',
    's_decperflevel',
    's_ttracedata',
]

SMRD = [
    's_load_dword',
    's_load_dwordx2',
    's_load_dwordx4',
    's_load_dwordx8',
    's_load_dwordx16',
    's_buffer_load_dword',
    's_buffer_load_dwordx2',
    's_buffer_load_dwordx4',
    's_buffer_load_dwordx8',
    's_buffer_load_dwordx16',
    's_memtime',
    's_dcache_inv',
]

VOP2 = [
    'v_cndmask_b32',
    'v_readlane_b32',
    'v_writelane_b32',
    'v_add_f32',
    'v_sub_f32',
    'v_subrev_f32',
    'v_mac_legacy_f32',
    'v_mul_legacy_f32',
    'v_mul_f32',
    'v_mul_i32_i24',
    'v_mul_hi_i32_i24',
    'v_mul_u32_u24',
    'v_mul_hi_u32_u24',
    'v_min_legacy_f32',
    'v_max_legacy_f32',
    'v_min_f32',
    'v_max_f32',
    'v_min_i32',
    'v_max_i32',
    'v_min_u32',
    'v_max_u32',
    'v_lshr_b32',
    'v_lshrrev_b32',
    'v_ashr_i32',
    'v_ashrrev_i32',
    'v_lshl_b32',
    'v_lshlrev_b32',
    'v_and_b32',
    'v_or_b32',
    'v_xor_b32',
    'v_bfm_b32',
    'v_mac_f32',
    'v_madmk_f32',
    'v_madak_f32',
    'v_bcnt_u32_b32',
    'v_mbcnt_lo_u32_b32',
    'v_mbcnt_hi_u32_b32',
    'v_add_i32',
    'v_sub_i32',
    'v_subrev_i32',
    'v_addc_u32',
    'v_subb_u32',
    'v_subbrev_u32',
    'v_ldexp_f32',
    'v_cvt_pkaccum_u8_f32',
    'v_cvt_pknorm_i16_f32',
    'v_cvt_pknorm_u16_f32',
    'v_cvt_pkrtz_f16_f32',
    'v_cvt_pk_u16_u32',
    'v_cvt_pk_i16_i32',
]


VOP1 = [
    'v_nop',
    'v_mov_b32',
    'v_readfirstlane_b32',
    'v_cvt_i32_f64',
    'v_cvt_f64_i32',
    'v_cvt_f32_i32',
    'v_cvt_f32_u32',
    'v_cvt_u32_f32',
    'v_cvt_i32_f32',
    'v_mov_fed_b32',
    'v_cvt_f16_f32',
    'v_cvt_f32_f16',
    'v_cvt_rpi_i32_f32',
    'v_cvt_flr_i32_f32',
    'v_cvt_off_f32_i4',
    'v_cvt_f32_f64',
    'v_cvt_f64_f32',
    'v_cvt_f32_ubyte0',
    'v_cvt_f32_ubyte1',
    'v_cvt_f32_ubyte2',
    'v_cvt_f32_ubyte3',
    'v_cvt_u32_f64',
    'v_cvt_f64_u32',
    'v_fract_f32',
    'v_trunc_f32',
    'v_ceil_f32',
    'v_rndne_f32',
    'v_floor_f32',
    'v_exp_f32',
    'v_log_clamp_f32',
    'v_log_f32',
    'v_rcp_clamp_f32',
    'v_rcp_legacy_f32',
    'v_rcp_f32',
    'v_rcp_iflag_f32',
    'v_rsq_clamp_f32',
    'v_rsq_legacy_f32',
    'v_rsq_f32',
    'v_rcp_f64',
    'v_rcp_clamp_f64',
    'v_rsq_f64',
    'v_rsq_clamp_f64',
    'v_sqrt_f32',
    'v_sqrt_f64',
    'v_sin_f32',
    'v_cos_f32',
    'v_not_b32',
    'v_bfrev_b32',
    'v_ffbh_u32',
    'v_ffbl_b32',
    'v_ffbh_i32',
    'v_frexp_exp_i32_f64',
    'v_frexp_mant_f64',
    'v_fract_f64',
    'v_frexp_exp_i32_f32',
    'v_frexp_mant_f32',
    'v_clrexcp',
    'v_movreld_b32',
    'v_movrels_b32',
    'v_movrelsd_b32',
]

VOPC = [
    'v_cmp_f_f32',
    'v_cmp_lt_f32',
    'v_cmp_eq_f32',
    'v_cmp_le_f32',
    'v_cmp_gt_f32',
    'v_cmp_lg_f32',
    'v_cmp_ge_f32',
    'v_cmp_u_f32',
    'v_cmp_o_f32',
    'v_cmp_nge_f32',
    'v_cmp_nlg_f32',
    'v_cmp_ngt_f32',
    'v_cmp_nle_f32',
    'v_cmp_neq_f32',
    'v_cmp_nlt_f32',
    'v_cmp_tru_f32',
    'v_cmp_f_f64',
    'v_cmp_lt_f64',
    'v_cmp_eq_f64',
    'v_cmp_le_f64',
    'v_cmp_gt_f64',
    'v_cmp_lg_f64',
    'v_cmp_ge_f64',
    'v_cmp_u_f64',
    'v_cmp_o_f64',
    'v_cmp_nge_f64',
    'v_cmp_nlg_f64',
    'v_cmp_ngt_f64',
    'v_cmp_nle_f64',
    'v_cmp_neq_f64',
    'v_cmp_nlt_f64',
    'v_cmp_tru_f64',
    'v_cmpx_f_f64',
    'v_cmpx_lt_f64',
    'v_cmpx_eq_f64',
    'v_cmpx_le_f64',
    'v_cmpx_gt_f64',
    'v_cmpx_lg_f64',
    'v_cmpx_ge_f64',
    'v_cmpx_u_f64',
    'v_cmpx_o_f64',
    'v_cmpx_nge_f64',
    'v_cmpx_nlg_f64',
    'v_cmpx_ngt_f64',
    'v_cmpx_nle_f64',
    'v_cmpx_neq_f64',
    'v_cmpx_nlt_f64',
    'v_cmpx_tru_f64',
    'v_cmps_f_f32',
    'v_cmps_lt_f32',
    'v_cmps_eq_f32',
    'v_cmps_le_f32',
    'v_cmps_gt_f32',
    'v_cmps_lg_f32',
    'v_cmps_ge_f32',
    'v_cmps_u_f32',
    'v_cmps_o_f32',
    'v_cmps_nge_f32',
    'v_cmps_nlg_f32',
    'v_cmps_ngt_f32',
    'v_cmps_nle_f32',
    'v_cmps_neq_f32',
    'v_cmps_nlt_f32',
    'v_cmps_tru_f32',
    'v_cmpsx_f_f32',
    'v_cmpsx_lt_f32',
    'v_cmpsx_eq_f32',
    'v_cmpsx_le_f32',
    'v_cmpsx_gt_f32',
    'v_cmpsx_lg_f32',
    'v_cmpsx_ge_f32',
    'v_cmpsx_u_f32',
    'v_cmpsx_o_f32',
    'v_cmpsx_nge_f32',
    'v_cmpsx_nlg_f32',
    'v_cmpsx_ngt_f32',
    'v_cmpsx_nle_f32',
    'v_cmpsx_neq_f32',
    'v_cmpsx_nlt_f32',
    'v_cmpsx_tru_f32',
    'v_cmps_f_f64',
    'v_cmps_lt_f64',
    'v_cmps_eq_f64',
    'v_cmps_le_f64',
    'v_cmps_gt_f64',
    'v_cmps_lg_f64',
    'v_cmps_ge_f64',
    'v_cmps_u_f64',
    'v_cmps_o_f64',
    'v_cmps_nge_f64',
    'v_cmps_nlg_f64',
    'v_cmps_ngt_f64',
    'v_cmps_nle_f64',
    'v_cmps_neq_f64',
    'v_cmps_nlt_f64',
    'v_cmps_tru_f64',
    'v_cmpsx_f_f64',
    'v_cmpsx_lt_f64',
    'v_cmpsx_eq_f64',
    'v_cmpsx_le_f64',
    'v_cmpsx_gt_f64',
    'v_cmpsx_lg_f64',
    'v_cmpsx_ge_f64',
    'v_cmpsx_u_f64',
    'v_cmpsx_o_f64',
    'v_cmpsx_nge_f64',
    'v_cmpsx_nlg_f64',
    'v_cmpsx_ngt_f64',
    'v_cmpsx_nle_f64',
    'v_cmpsx_neq_f64',
    'v_cmpsx_nlt_f64',
    'v_cmpsx_tru_f64',
    'v_cmp_f_i32',
    'v_cmp_lt_i32',
    'v_cmp_eq_i32',
    'v_cmp_le_i32',
    'v_cmp_gt_i32',
    'v_cmp_lg_i32',
    'v_cmp_ge_i32',
    'v_cmp_o_i32',
    'v_cmp_u_i32',
    'v_cmp_nge_i32',
    'v_cmp_nlg_i32',
    'v_cmp_ngt_i32',
    'v_cmp_nle_i32',
    'v_cmp_ne_i32',
    'v_cmp_nlt_i32',
    'v_cmp_tru_i32',
    'v_cmpx_f_i32',
    'v_cmpx_lt_i32',
    'v_cmpx_eq_i32',
    'v_cmpx_le_i32',
    'v_cmpx_gt_i32',
    'v_cmpx_lg_i32',
    'v_cmpx_ge_i32',
    'v_cmpx_o_i32',
    'v_cmpx_u_i32',
    'v_cmpx_nge_i32',
    'v_cmpx_nlg_i32',
    'v_cmpx_ngt_i32',
    'v_cmpx_nle_i32',
    'v_cmpx_ne_i32',
    'v_cmpx_nlt_i32',
    'v_cmpx_tru_i32',
    'v_cmp_f_i64',
    'v_cmp_lt_i64',
    'v_cmp_eq_i64',
    'v_cmp_le_i64',
    'v_cmp_gt_i64',
    'v_cmp_lg_i64',
    'v_cmp_ge_i64',
    'v_cmp_o_i64',
    'v_cmp_u_i64',
    'v_cmp_nge_i64',
    'v_cmp_nlg_i64',
    'v_cmp_ngt_i64',
    'v_cmp_nle_i64',
    'v_cmp_ne_i64',
    'v_cmp_nlt_i64',
    'v_cmp_tru_i64',
    'v_cmpx_f_i64',
    'v_cmpx_lt_i64',
    'v_cmpx_eq_i64',
    'v_cmpx_le_i64',
    'v_cmpx_gt_i64',
    'v_cmpx_lg_i64',
    'v_cmpx_ge_i64',
    'v_cmpx_o_i64',
    'v_cmpx_u_i64',
    'v_cmpx_nge_i64',
    'v_cmpx_nlg_i64',
    'v_cmpx_ngt_i64',
    'v_cmpx_nle_i64',
    'v_cmpx_ne_i64',
    'v_cmpx_nlt_i64',
    'v_cmpx_tru_i64',
    'v_cmp_f_u32',
    'v_cmp_lt_u32',
    'v_cmp_eq_u32',
    'v_cmp_le_u32',
    'v_cmp_gt_u32',
    'v_cmp_lg_u32',
    'v_cmp_ge_u32',
    'v_cmp_o_u32',
    'v_cmp_u_u32',
    'v_cmp_nge_u32',
    'v_cmp_nlg_u32',
    'v_cmp_ngt_u32',
    'v_cmp_nle_u32',
    'v_cmp_ne_u32',
    'v_cmp_nlt_u32',
    'v_cmp_tru_u32',
    'v_cmpx_f_u32',
    'v_cmpx_lt_u32',
    'v_cmpx_eq_u32',
    'v_cmpx_le_u32',
    'v_cmpx_gt_u32',
    'v_cmpx_lg_u32',
    'v_cmpx_ge_u32',
    'v_cmpx_o_u32',
    'v_cmpx_u_u32',
    'v_cmpx_nge_u32',
    'v_cmpx_nlg_u32',
    'v_cmpx_ngt_u32',
    'v_cmpx_nle_u32',
    'v_cmpx_ne_u32',
    'v_cmpx_nlt_u32',
    'v_cmpx_tru_u32',
    'v_cmp_f_u64',
    'v_cmp_lt_u64',
    'v_cmp_eq_u64',
    'v_cmp_le_u64',
    'v_cmp_gt_u64',
    'v_cmp_lg_u64',
    'v_cmp_ge_u64',
    'v_cmp_o_u64',
    'v_cmp_u_u64',
    'v_cmp_nge_u64',
    'v_cmp_nlg_u64',
    'v_cmp_ngt_u64',
    'v_cmp_nle_u64',
    'v_cmp_ne_u64',
    'v_cmp_nlt_u64',
    'v_cmp_tru_u64',
    'v_cmpx_f_u64',
    'v_cmpx_lt_u64',
    'v_cmpx_eq_u64',
    'v_cmpx_le_u64',
    'v_cmpx_gt_u64',
    'v_cmpx_lg_u64',
    'v_cmpx_ge_u64',
    'v_cmpx_o_u64',
    'v_cmpx_u_u64',
    'v_cmpx_nge_u64',
    'v_cmpx_nlg_u64',
    'v_cmpx_ngt_u64',
    'v_cmpx_nle_u64',
    'v_cmpx_ne_u64',
    'v_cmpx_nlt_u64',
    'v_cmpx_tru_u64',
]

VOP3A = [
    'v_mad_legacy_f32',
    'v_mad_f32',
    'v_mad_i32_i24',
    'v_mad_u32_u24',
    'v_cubeid_f32',
    'v_cubesc_f32',
    'v_cubetc_f32',
    'v_cubema_f32',
    'v_bfe_u32',
    'v_bfe_i32',
    'v_bfi_b32',
    'v_fma_f32',
    'v_fma_f64',
    'v_lerp_u8',
    'v_alignbit_b32',
    'v_alignbyte_b32',
    'v_mullit_f32',
    'v_min3_f32',
    'v_min3_i32',
    'v_min3_u32',
    'v_max3_f32',
    'v_max3_i32',
    'v_max3_u32',
    'v_med3_f32',
    'v_med3_i32',
    'v_med3_u32',
    'v_sad_u8',
    'v_sad_hi_u8',
    'v_sad_u16',
    'v_sad_u32',
    'v_cvt_pk_u8_f32',
    'v_div_fixup_f32',
    'v_div_fixup_f64',
    'v_lshl_b64',
    'v_lshr_b64',
    'v_ashr_i64',
    'v_add_f64',
    'v_mul_f64',
    'v_min_f64',
    'v_max_f64',
    'v_ldexp_f64',
    'v_mul_lo_u32',
    'v_mul_hi_u32',
    'v_mul_lo_i32',
    'v_mul_hi_i32',
    'v_div_fmas_f32',
    'v_div_fmas_f64',
    'v_msad_u8',
    'v_qsad_u8',
    'v_mqsad_u8',
    'v_trig_preop_f64',
]

VOP3B = [
    'v_div_scale_f32',
    'v_div_scale_f64',
]

VINTRP = [
    'v_interp_p1_f32',
    'v_interp_p2_f32',
    'v_interp_mov_f32',
]

LDS = [
    'ds_add_u32',
    'ds_sub_u32',
    'ds_rsub_u32',
    'ds_inc_u32',
    'ds_dec_u32',
    'ds_min_i32',
    'ds_max_i32',
    'ds_min_u32',
    'ds_max_u32',
    'ds_and_b32',
    'ds_or_b32',
    'ds_xor_b32',
    'ds_mskor_b32',
    'ds_write_b32',
    'ds_write2_b32',
    'ds_write2st64_b32',
    'ds_cmpst_b32',
    'ds_cmpst_f32',
    'ds_min_f32',
    'ds_max_f32',
    'ds_gws_init',
    'ds_gws_sema_v',
    'ds_gws_sema_br',
    'ds_gws_sema_p',
    'ds_gws_barrier',
    'ds_write_b8',
    'ds_write_b16',
    'ds_add_rtn_u32',
    'ds_sub_rtn_u32',
    'ds_rsub_rtn_u32',
    'ds_inc_rtn_u32',
    'ds_dec_rtn_u32',
    'ds_min_rtn_i32',
    'ds_max_rtn_i32',
    'ds_min_rtn_u32',
    'ds_max_rtn_u32',
    'ds_and_rtn_b32',
    'ds_or_rtn_b32',
    'ds_xor_rtn_b32',
    'ds_mskor_rtn_b32',
    'ds_wrxchg_rtn_b32',
    'ds_wrxchg2st64_rtn_b32',
    'ds_cmpst_rtn_b32',
    'ds_cmpst_rtn_f32',
    'ds_min_rtn_f32',
    'ds_max_rtn_f32',
    'ds_write2st64_b32',
    'ds_cmpst_b32',
    'ds_cmpst_f32',
    'ds_min_f32',
    'ds_max_f32',
    'ds_gws_init',
    'ds_gws_sema_v',
    'ds_gws_sema_br',
    'ds_gws_sema_p',
    'ds_gws_barrier',
    'ds_write_b8',
    'ds_write_b16',
    'ds_add_rtn_u32',
    'ds_sub_rtn_u32',
    'ds_rsub_rtn_u32',
    'ds_inc_rtn_u32',
    'ds_dec_rtn_u32',
    'ds_min_rtn_i32',
    'ds_max_rtn_i32',
    'ds_min_rtn_u32',
    'ds_max_rtn_u32',
    'ds_and_rtn_b32',
    'ds_or_rtn_b32',
    'ds_xor_rtn_b32',
    'ds_mskor_rtn_b32',
    'ds_wrxchg_rtn_b32',
    'ds_wrxchg2_rtn_b32',
    'ds_wrxchg2st64_rtn_b32',
    'ds_cmpst_rtn_b32',
    'ds_cmpst_rtn_f32',
    'ds_min_rtn_f32',
    'ds_max_rtn_f32',
    'ds_swizzle_b32',
    'ds_read_b32',
    'ds_read2_b32',
    'ds_read2st64_b32',
    'ds_read_i8',
    'ds_read_u8',
    'ds_read_i16',
    'ds_read_u16',
    'ds_consume',
    'ds_append',
    'ds_ordered_count',
    'ds_add_u64',
    'ds_sub_u64',
    'ds_rsub_u64',
    'ds_inc_u64',
    'ds_dec_u64',
    'ds_min_i64',
    'ds_max_i64',
    'ds_min_u64',
    'ds_max_u64',
    'ds_and_b64',
    'ds_or_b64',
    'ds_xor_b64',
    'ds_mskor_b64',
    'ds_write_b64',
    'ds_write2_b64',
    'ds_write2st64_b64',
    'ds_cmpst_b64',
    'ds_cmpst_f64',
    'ds_min_f64',
    'ds_max_f64',
    'ds_add_rtn_u64',
    'ds_sub_rtn_u64',
    'ds_rsub_rtn_u64',
    'ds_inc_rtn_u64',
    'ds_dec_rtn_u64',
    'ds_min_rtn_i64',
    'ds_max_rtn_i64',
    'ds_min_rtn_u64',
    'ds_max_rtn_u64',
    'ds_and_rtn_b64',
    'ds_or_rtn_b64',
    'ds_xor_rtn_b64',
    'ds_mskor_rtn_b64',
    'ds_wrxchg_rtn_b64',
    'ds_wrxchg2_rtn_b64',
    'ds_wrxchg2st64_rtn_b64',
    'ds_cmpst_rtn_b64',
    'ds_cmpst_rtn_f64',
    'ds_min_rtn_f64',
    'ds_max_rtn_f64',
    'ds_read_b64',
    'ds_read2_b64',
    'ds_read2st64_b64',
    'ds_add_src2_u32',
    'ds_sub_src2_u32',
    'ds_rsub_src2_u32',
    'ds_inc_src2_u32',
    'ds_dec_src2_u32',
    'ds_min_src2_i32',
    'ds_max_src2_i32',
    'ds_min_src2_u32',
    'ds_max_src2_u32',
    'ds_and_src2_b32',
    'ds_or_src2_b32',
    'ds_xor_src2_b32',
    'ds_write_src2_b32',
    'ds_min_src2_f32',
    'ds_max_src2_f32',
    'ds_add_src2_u64',
    'ds_sub_src2_u64',
    'ds_rsub_src2_u64',
    'ds_inc_src2_u64',
    'ds_dec_src2_u64',
    'ds_min_src2_i64',
    'ds_max_src2_i64',
    'ds_min_src2_u64',
    'ds_max_src2_u64',
    'ds_and_src2_b64',
    'ds_or_src2_b64',
    'ds_xor_src2_b64',
    'ds_write_src2_b64',
    'ds_min_src2_f64',
    'ds_max_src2_f64',
]

MUBUF = [
    'buffer_load_format_x',
    'buffer_load_format_xy',
    'buffer_load_format_xyz',
    'buffer_load_format_xyzw',
    'buffer_store_format_x',
    'buffer_store_format_xy',
    'buffer_store_format_xyz',
    'buffer_store_format_xyzw',
    'buffer_load_ubyte',
    'buffer_load_sbyte',
    'buffer_load_ushort',
    'buffer_load_sshort',
    'buffer_load_dword',
    'buffer_load_dwordx2',
    'buffer_load_dwordx4',
    'buffer_store_byte',
    'buffer_store_short',
    'buffer_store_dword',
    'buffer_store_dwordx2',
    'buffer_store_dwordx4',
    'buffer_atomic_swap',
    'buffer_atomic_cmpswap',
    'buffer_atomic_add',
    'buffer_atomic_sub',
    'buffer_atomic_rsub',
    'buffer_atomic_smin',
    'buffer_atomic_umin',
    'buffer_atomic_smax',
    'buffer_atomic_umax',
    'buffer_atomic_and',
    'buffer_atomic_or',
    'buffer_atomic_xor',
    'buffer_atomic_inc',
    'buffer_atomic_dec',
    'buffer_atomic_fcmpswap',
    'buffer_atomic_fmin',
    'buffer_atomic_fmax',
    'buffer_atomic_swap_x2',
    'buffer_atomic_cmpswap_x2',
    'buffer_atomic_add_x2',
    'buffer_atomic_sub_x2',
    'buffer_atomic_rsub_x2',
    'buffer_atomic_smin_x2',
    'buffer_atomic_umin_x2',
    'buffer_atomic_smax_x2',
    'buffer_atomic_umax_x2',
    'buffer_atomic_and_x2',
    'buffer_atomic_or_x2',
    'buffer_atomic_xor_x2',
    'buffer_atomic_inc_x2',
    'buffer_atomic_dec_x2',
    'buffer_atomic_fcmpswap_x2',
    'buffer_atomic_fmin_x2',
    'buffer_atomic_fmax_x2',
    'buffer_wbinvl1_sc',
    'buffer_wbinvl1',
]

MTBUF = [
    'tbuffer_load_format_x',
    'tbuffer_load_format_xy',
    'tbuffer_load_format_xyz',
    'tbuffer_load_format_xyzw',
    'tbuffer_store_format_x',
    'tbuffer_store_format_xy',
    'tbuffer_store_format_xyz',
    'tbuffer_store_format_xyzw',
]

MIMG = [
    'image_load',
    'image_load_mip',
    'image_load_pck',
    'image_load_pck_sgn',
    'image_load_mip_pck',
    'image_load_mip_pck_sgn',
    'image_store',
    'image_store_mip',
    'image_store_pck',
    'image_store_mip_pck',
    'image_atomic_swap',
    'image_atomic_cmpswap',
    'image_atomic_add',
    'image_atomic_sub',
    'image_atomic_rsub',
    'image_atomic_smin',
    'image_atomic_umin',
    'image_atomic_smax',
    'image_atomic_umax',
    'image_atomic_and',
    'image_atomic_or',
    'image_atomic_xor',
    'image_atomic_inc',
    'image_atomic_dec',
    'image_atomic_fcmpswap',
    'image_atomic_fmin',
    'image_atomic_fmax',
    'image_sample',
    'image_sample_cl',
    'image_sample_d',
    'image_sample_d_cl',
    'image_sample_l',
    'image_sample_b',
    'image_sample_b_cl',
    'image_sample_lz',
    'image_sample_c',
    'image_sample_c_cl',
    'image_sample_c_d',
    'image_sample_c_d_cl',
    'image_sample_c_l',
    'image_sample_c_b',
    'image_sample_c_b_cl',
    'image_sample_c_lz',
    'image_sample_o',
    'image_sample_cl_o',
    'image_sample_d_o',
    'image_sample_d_cl_o',
    'image_sample_l_o',
    'image_sample_b_o',
    'image_sample_b_cl_o',
    'image_sample_lz_o',
    'image_sample_c_o',
    'image_sample_c_cl_o',
    'image_sample_c_d_o',
    'image_sample_c_d_cl_o',
    'image_sample_c_l_o',
    'image_sample_c_b_o',
    'image_sample_c_b_cl_o',
    'image_sample_c_lz_o',
    'image_sample_cd',
    'image_sample_cd_cl',
    'image_sample_c_cd',
    'image_sample_c_cd_cl',
    'image_sample_cd_o',
    'image_sample_cd_cl_o',
    'image_sample_c_cd_o',
    'image_sample_c_cd_cl_o',
    'image_gather4',
    'image_gather4_cl',
    'image_gather4_l',
    'image_gather4_b',
    'image_gather4_b_cl',
    'image_gather4_lz',
    'image_gather4_c',
    'image_gather4_c_cl',
    'image_gather4_c_l',
    'image_gather4_c_b',
    'image_gather4_c_b_cl',
    'image_gather4_c_lz',
    'image_gather4_o',
    'image_gather4_cl_o',
    'image_gather4_l_o',
    'image_gather4_b_o',
    'image_gather4_b_cl_o',
    'image_gather4_lz_o',
    'image_gather4_c_o',
    'image_gather4_c_cl_o',
    'image_gather4_c_l_o',
    'image_gather4_c_b_o',
    'image_gather4_c_b_cl_o',
    'image_gather4_c_lz_o',
    'image_get_resinfo',
    'image_get_lod',
]

EXP = [
    'export'
]

ISA = {}
ISA['SOP2'] = SOP2
ISA['SOPK'] = SOPK
ISA['SOP1'] = SOP1
ISA['SOPC'] = SOPC
ISA['SOPP'] = SOPP
ISA['SMRD'] = SMRD
ISA['VOP2'] = VOP2
ISA['VOP1'] = VOP1
ISA['VOPC'] = VOPC
ISA['VOP3A'] = VOP3A
ISA['VOP3B'] = VOP3B
ISA['VINTRP'] = VINTRP
ISA['LDS'] = LDS
ISA['MUBUF'] = MUBUF
ISA['MTBUF'] = MTBUF
ISA['MIMG'] = MIMG
ISA['EXP'] = EXP


class InstructionInfo(object):
    """docstring for InstructionInfo"""

    def __init__(self):
        self.__inst_dict = {}

        # Build dictionary
        for key, value in ISA.iteritems():
            for item in value:
                # Decide type
                if key.startswith('S'):
                    inst_type = 'scalar'
                else:
                    inst_type = 'vector'

                # Decide execution unit
                if 'branch' in item:
                    exec_unit = 'branch'
                    exec_cost = 5
                elif key == 'LDS':
                    exec_unit = 'lds'
                    exec_cost = 20
                elif inst_type == 'scalar':
                    exec_unit = 'scalar'
                    exec_cost = 5
                elif key in ['MUBUF', 'MTBUF', 'MIMG']:
                    exec_unit = 'vector mem'
                    exec_cost = 100
                else:
                    exec_unit = 'simd'
                    exec_cost = 5
                self.__inst_dict[item] = (key, inst_type, exec_unit, exec_cost)

    def get_info(self, instruction):
        """ Get information of given instruction """
        return self.__inst_dict[instruction]
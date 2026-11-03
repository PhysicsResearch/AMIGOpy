# -*- coding: utf-8 -*-
"""
tab_evaluation.py - "Evaluation" tab of the View module (before MonteCarlo)
==========================================================================
Sub-tabs (on top, like the MonteCarlo tab):
    * Isodoses: isodose templates (levels, colours, unit) and up to 4 doses drawn on the views,
      each with its line style and width (fcn_evaluation.isodose)
    * Gamma: gamma analysis of two doses, 2D or 3D, criteria table, result saved as a series of
      modality Gamma (fcn_evaluation.gamma_panel)
"""
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QDoubleSpinBox, QGridLayout, QGroupBox,
                               QHBoxLayout, QHeaderView, QLabel, QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
                               QTabWidget, QTableWidget, QVBoxLayout, QWidget)

from fcn_evaluation.isodose import LINE_STYLES, N_SLOTS


class SeriesCombo(QComboBox):
    """A combo of dose series whose list is refreshed (on_popup) right before it opens."""
    on_popup = None

    def showPopup(self):
        if self.on_popup is not None:
            self.on_popup()
        super().showPopup()


def _group(parent, title, accent):
    gb = QGroupBox(title, parent)
    gb.setStyleSheet(f"QGroupBox {{ border: 1px solid {accent}; border-radius: 4px; margin-top: 8px; font-weight: bold; }}"
                     f"QGroupBox::title {{ color: {accent}; subcontrol-origin: margin; left: 8px; padding: 0 3px; }}")
    return gb


def _button(parent, name, text, tip, w):
    btn = QPushButton(text, parent)
    btn.setObjectName(name)
    btn.setToolTip(tip)
    setattr(w, name, btn)
    return btn


def create_tab_evaluation(w):
    """Build the Evaluation tab (w.tab_evaluation) and initialize its panels."""
    w.tab_evaluation = QWidget()
    w.tab_evaluation.setObjectName(u"tab_evaluation")
    outer = QGridLayout(w.tab_evaluation)
    outer.setObjectName(u"gridLayout_eval_outer")
    w.eval_tabs = QTabWidget(w.tab_evaluation)
    w.eval_tabs.setObjectName(u"eval_tabs")
    w.eval_tabs.setTabPosition(QTabWidget.TabPosition.North)
    outer.addWidget(w.eval_tabs, 0, 0, 1, 1)
    _create_isodose_tab(w)
    _create_gamma_tab(w)
    w.eval_tabs.setCurrentIndex(0)

    from fcn_evaluation.gamma_panel import init_gamma_panel
    from fcn_evaluation.isodose import init_isodose_panel
    init_isodose_panel(w)
    init_gamma_panel(w)


def _create_isodose_tab(w):
    w.eval_tab_isodose = QWidget()
    w.eval_tab_isodose.setObjectName(u"eval_tab_isodose")
    grid = QGridLayout(w.eval_tab_isodose)

    # --- levels (template) ---------------------------------------------------
    gb = _group(w.eval_tab_isodose, u"Isodose levels", "#50e3c2")
    gb.setObjectName(u"iso_levels_group")
    v = QVBoxLayout(gb)
    row = QHBoxLayout()
    row.addWidget(QLabel(u"Template:", gb))
    w.iso_template_combo = QComboBox(gb)
    w.iso_template_combo.setObjectName(u"iso_template_combo")
    w.iso_template_combo.setMinimumWidth(140)
    row.addWidget(w.iso_template_combo, 1)
    for name, text, tip in (("iso_new_btn", u"New", u"New isodose template (one level, 100 %)"),
                            ("iso_dup_btn", u"Duplicate", u"Copy of the template shown under a new name"),
                            ("iso_rename_btn", u"Rename", u"Rename the template shown"),
                            ("iso_del_btn", u"Delete", u"Delete the template shown")):
        row.addWidget(_button(gb, name, text, tip, w))
    v.addLayout(row)

    row = QHBoxLayout()
    row.addWidget(QLabel(u"Unit:", gb))
    w.iso_unit_combo = QComboBox(gb)
    w.iso_unit_combo.setObjectName(u"iso_unit_combo")
    w.iso_unit_combo.addItems([u"% of reference", u"Gy"])
    w.iso_unit_combo.setToolTip(u"Levels in % of the reference dose, or in Gy")
    row.addWidget(w.iso_unit_combo)
    row.addWidget(QLabel(u"Reference:", gb))
    w.iso_ref_spin = QDoubleSpinBox(gb)
    w.iso_ref_spin.setObjectName(u"iso_ref_spin")
    w.iso_ref_spin.setRange(0.001, 100000.0)
    w.iso_ref_spin.setDecimals(3)
    w.iso_ref_spin.setSuffix(u" Gy")
    w.iso_ref_spin.setToolTip(u"Dose of 100 % (e.g. the prescription), saved with the template")
    row.addWidget(w.iso_ref_spin)
    row.addStretch(1)
    v.addLayout(row)

    w.iso_levels_table = QTableWidget(0, 3, gb)
    w.iso_levels_table.setObjectName(u"iso_levels_table")
    w.iso_levels_table.setHorizontalHeaderLabels([u"Show", u"Value", u"Colour"])
    w.iso_levels_table.verticalHeader().setVisible(False)
    head = w.iso_levels_table.horizontalHeader()
    head.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
    head.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
    head.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
    w.iso_levels_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    w.iso_levels_table.setToolTip(u"Isodose levels: tick to show, type the value, click the colour to change it.\n"
                                  u"Changes are saved to the template shown.")
    v.addWidget(w.iso_levels_table, 1)
    row = QHBoxLayout()
    row.addWidget(_button(gb, "iso_add_level_btn", u"Add level", u"Add a level after the selected one", w))
    row.addWidget(_button(gb, "iso_del_level_btn", u"Remove level", u"Remove the selected level(s)", w))
    row.addStretch(1)
    v.addLayout(row)
    grid.addWidget(gb, 0, 0, 1, 1)

    # --- doses (up to N_SLOTS) -------------------------------------------------
    gb = _group(w.eval_tab_isodose, u"Doses (up to 4, compared with the same levels)", "#f5a623")
    gb.setObjectName(u"iso_doses_group")
    g = QGridLayout(gb)
    w.iso_show_chk = QCheckBox(u"Show isodoses on the views", gb)
    w.iso_show_chk.setObjectName(u"iso_show_chk")
    w.iso_show_chk.setChecked(True)
    g.addWidget(w.iso_show_chk, 0, 0, 1, 4)
    for c, text in enumerate((u"", u"Dose (RTDOSE / MCNP of the patient shown)", u"Line", u"Width")):
        g.addWidget(QLabel(text, gb), 1, c)
    for i in range(N_SLOTS):
        show = QCheckBox(f"{i + 1}", gb)
        show.setObjectName(f"iso_slot{i}_show")
        show.setChecked(True)
        series = SeriesCombo(gb)
        series.setObjectName(f"iso_slot{i}_series")
        series.setMinimumWidth(220)
        series.addItem(u"(none)", None)
        style = QComboBox(gb)
        style.setObjectName(f"iso_slot{i}_style")
        style.addItems(list(LINE_STYLES))
        width = QDoubleSpinBox(gb)
        width.setObjectName(f"iso_slot{i}_width")
        width.setRange(0.5, 10.0)
        width.setSingleStep(0.5)
        width.setDecimals(1)
        width.setValue(2.0)
        for name, widget in (("show", show), ("series", series), ("style", style), ("width", width)):
            setattr(w, f"iso_slot{i}_{name}", widget)
        for c, widget in enumerate((show, series, style, width)):
            g.addWidget(widget, i + 2, c)
    g.setColumnStretch(1, 1)
    g.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), N_SLOTS + 2, 0)
    grid.addWidget(gb, 0, 1, 1, 1)
    grid.setColumnStretch(0, 1)
    grid.setColumnStretch(1, 1)
    w.eval_tabs.addTab(w.eval_tab_isodose, u"Isodoses")


def _create_gamma_tab(w):
    w.eval_tab_gamma = QWidget()
    w.eval_tab_gamma.setObjectName(u"eval_tab_gamma")
    grid = QGridLayout(w.eval_tab_gamma)

    # --- doses and mode --------------------------------------------------------
    gb = _group(w.eval_tab_gamma, u"Doses", "#50e3c2")
    g = QGridLayout(gb)
    g.addWidget(QLabel(u"Reference:", gb), 0, 0)
    w.gamma_ref_combo = SeriesCombo(gb)
    w.gamma_ref_combo.setObjectName(u"gamma_ref_combo")
    w.gamma_ref_combo.setMinimumWidth(220)
    w.gamma_ref_combo.setToolTip(u"Reference dose: the gamma is computed at its voxels (or on the evaluation grid)")
    g.addWidget(w.gamma_ref_combo, 0, 1, 1, 3)
    g.addWidget(QLabel(u"Evaluated:", gb), 1, 0)
    w.gamma_eval_combo = SeriesCombo(gb)
    w.gamma_eval_combo.setObjectName(u"gamma_eval_combo")
    w.gamma_eval_combo.setToolTip(u"Evaluated dose: interpolated (trilinear) by patient position")
    g.addWidget(w.gamma_eval_combo, 1, 1, 1, 3)
    g.addWidget(QLabel(u"Mode:", gb), 2, 0)
    w.gamma_mode_combo = QComboBox(gb)
    w.gamma_mode_combo.setObjectName(u"gamma_mode_combo")
    w.gamma_mode_combo.addItems([u"3D (volume)", u"2D (plane shown)"])
    g.addWidget(w.gamma_mode_combo, 2, 1)
    g.addWidget(QLabel(u"Plane:", gb), 2, 2)
    w.gamma_plane_combo = QComboBox(gb)
    w.gamma_plane_combo.setObjectName(u"gamma_plane_combo")
    w.gamma_plane_combo.addItems([u"Axial", u"Coronal", u"Sagittal"])
    w.gamma_plane_combo.setToolTip(u"2D: the plane shown in this view (its current slice)")
    g.addWidget(w.gamma_plane_combo, 2, 3)
    g.setColumnStretch(1, 1)
    grid.addWidget(gb, 0, 0, 1, 1)

    # --- parameters ------------------------------------------------------------
    gb = _group(w.eval_tab_gamma, u"Parameters", "#f5a623")
    g = QGridLayout(gb)
    g.addWidget(QLabel(u"Normalization dose:", gb), 0, 0)
    w.gamma_norm_combo = QComboBox(gb)
    w.gamma_norm_combo.setObjectName(u"gamma_norm_combo")
    w.gamma_norm_combo.addItems([u"Max of reference", u"Dose (Gy)"])
    w.gamma_norm_combo.setToolTip(u"Global dose difference and threshold are % of this dose")
    g.addWidget(w.gamma_norm_combo, 0, 1)
    w.gamma_norm_spin = QDoubleSpinBox(gb)
    w.gamma_norm_spin.setObjectName(u"gamma_norm_spin")
    w.gamma_norm_spin.setRange(0.001, 100000.0)
    w.gamma_norm_spin.setDecimals(3)
    w.gamma_norm_spin.setValue(7.0)
    w.gamma_norm_spin.setSuffix(u" Gy")
    g.addWidget(w.gamma_norm_spin, 0, 2)
    g.addWidget(QLabel(u"Max gamma:", gb), 1, 0)
    w.gamma_max_spin = QDoubleSpinBox(gb)
    w.gamma_max_spin.setObjectName(u"gamma_max_spin")
    w.gamma_max_spin.setRange(1.0, 10.0)
    w.gamma_max_spin.setSingleStep(0.5)
    w.gamma_max_spin.setDecimals(1)
    w.gamma_max_spin.setValue(2.0)
    w.gamma_max_spin.setToolTip(u"Search radius = max gamma x DTA; gammas above it are shown as max gamma")
    g.addWidget(w.gamma_max_spin, 1, 1)
    g.addWidget(QLabel(u"Step: DTA /", gb), 2, 0)
    w.gamma_fraction_spin = QSpinBox(gb)
    w.gamma_fraction_spin.setObjectName(u"gamma_fraction_spin")
    w.gamma_fraction_spin.setRange(2, 50)
    w.gamma_fraction_spin.setValue(10)
    w.gamma_fraction_spin.setToolTip(u"Sub-voxel search: distance step = DTA / this value (larger: finer and slower)")
    g.addWidget(w.gamma_fraction_spin, 2, 1)
    w.gamma_res_chk = QCheckBox(u"Evaluation grid (mm):", gb)
    w.gamma_res_chk.setObjectName(u"gamma_res_chk")
    w.gamma_res_chk.setToolTip(u"Compute the gamma on a grid of this spacing over the reference (else at the reference voxels)")
    g.addWidget(w.gamma_res_chk, 3, 0)
    w.gamma_res_spin = QDoubleSpinBox(gb)
    w.gamma_res_spin.setObjectName(u"gamma_res_spin")
    w.gamma_res_spin.setRange(0.1, 20.0)
    w.gamma_res_spin.setDecimals(2)
    w.gamma_res_spin.setValue(2.0)
    g.addWidget(w.gamma_res_spin, 3, 1)
    g.setColumnStretch(3, 1)
    grid.addWidget(gb, 1, 0, 1, 1)

    # --- criteria and results --------------------------------------------------
    gb = _group(w.eval_tab_gamma, u"Criteria", "#ffd900")
    v = QVBoxLayout(gb)
    w.gamma_table = QTableWidget(0, 9, gb)
    w.gamma_table.setObjectName(u"gamma_table")
    w.gamma_table.setHorizontalHeaderLabels([u"DD (%)", u"DTA (mm)", u"Thresh. (%)", u"Norm.",
                                             u"Pass (%)", u"Mean γ", u"γ 95 %", u"γ max", u"Points"])
    w.gamma_table.verticalHeader().setVisible(False)
    w.gamma_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    w.gamma_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
    w.gamma_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    w.gamma_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    w.gamma_table.setToolTip(u"Criteria: dose difference (%), distance to agreement (mm), lower dose threshold "
                             u"(% of the normalization dose), global or local.\nRun fills the results; Save stores "
                             u"the gamma of the selected row in the data tree (modality Gamma).")
    v.addWidget(w.gamma_table, 1)
    row = QHBoxLayout()
    row.addWidget(_button(gb, "gamma_add_btn", u"Add", u"Add a criterion", w))
    row.addWidget(_button(gb, "gamma_remove_btn", u"Remove", u"Remove the selected criterion", w))
    row.addStretch(1)
    row.addWidget(_button(gb, "gamma_run_btn", u"Run", u"Gamma of every criterion (Cancel in the progress window)", w))
    row.addWidget(_button(gb, "gamma_save_btn", u"Save selected", u"The gamma of the selected criterion as a new "
                                                                   u"series (modality Gamma) of the reference's study", w))
    v.addLayout(row)
    w.gamma_status = QLabel(u"-", gb)
    w.gamma_status.setObjectName(u"gamma_status")
    w.gamma_status.setWordWrap(True)
    v.addWidget(w.gamma_status)
    grid.addWidget(gb, 0, 1, 2, 1)
    grid.setRowStretch(1, 1)
    grid.setColumnStretch(0, 2)
    grid.setColumnStretch(1, 3)
    w.eval_tabs.addTab(w.eval_tab_gamma, u"Gamma")

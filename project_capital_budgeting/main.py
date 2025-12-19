import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QDoubleSpinBox, QSpinBox, QLineEdit,
    QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QStackedWidget
)
from PyQt6.QtWidgets import QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# -------------------------------------------------------------------------
# STYLING & THEME CONFIGURATION
# -------------------------------------------------------------------------
THEME = {
    "bg_dark": "#1e1e2e",       # Main Window BG
    "bg_lighter": "#2a2a3c",    # Card/Sidebar BG
    "accent": "#7f5af0",        # Main Purple Accent
    "secondary": "#2cb67d",     # Green Accent
    "text_main": "#fffffe",
    "text_dim": "#94a1b2",
    "button_hover": "#36364f"
}

STYLESHEET = f"""
QMainWindow {{
    background-color: {THEME['bg_dark']};
}}

/* Sidebar Styling */
QFrame#Sidebar {{
    background-color: {THEME['bg_lighter']};
    border-right: 1px solid #3f3f55;
}}
QLabel#AppLogo {{
    color: {THEME['accent']};
    font-weight: bold;
    font-size: 24px;
    padding: 20px;
}}
QPushButton.NavButton {{
    background-color: transparent;
    color: {THEME['text_dim']};
    text-align: left;
    padding: 15px 20px;
    border: none;
    font-size: 16px;
    border-left: 4px solid transparent;
}}
QPushButton.NavButton:hover {{
    background-color: {THEME['button_hover']};
    color: {THEME['text_main']};
}}
QPushButton.NavButton:checked {{
    color: {THEME['text_main']};
    border-left: 4px solid {THEME['accent']};
    background-color: {THEME['button_hover']};
}}

/* Dashboard Card Styling */
QFrame.SolverCard {{
    background-color: {THEME['bg_lighter']};
    border-radius: 15px;
    border: 1px solid #3f3f55;
}}
QFrame.SolverCard:hover {{
    border: 1px solid {THEME['accent']};
    background-color: {THEME['button_hover']};
}}
QLabel.CardTitle {{
    color: {THEME['text_main']};
    font-size: 20px;
    font-weight: bold;
}}
QLabel.CardDesc {{
    color: {THEME['text_dim']};
    font-size: 14px;
}}
QPushButton.CardButton {{
    background-color: {THEME['accent']};
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
}}
QPushButton.CardButton:hover {{
    background-color: #6a48c9;
}}
"""



class MplCanvas(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)


class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        t = QLabel("🏠 Bienvenue dans l'application Capital Budgeting")
        t.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(t)

        self.btn_data = QPushButton("📥 Entrer les données manuellement")
        self.btn_test1 = QPushButton("⚡ Test 1 – Petits projets")
        self.btn_test2 = QPushButton("🚀 Test 2 – Grand nombre de projets")

        layout.addWidget(self.btn_data)
        layout.addWidget(self.btn_test1)
        layout.addWidget(self.btn_test2)
        layout.addStretch()

        self.setLayout(layout)
        warning = QLabel(
            "⚠️ Remarque importante :\n"
            "Pour obtenir un résultat cohérent, tous les projets doivent avoir\n"
            "la même durée et la même unité temporelle (années / mois / trimestres).\n\n"
            "Le calcul automatique pour des durées différentes\n"
            "n'est pas encore disponible dans cette version."
        )

        warning.setStyleSheet("""
            color: #b30000;
            font-size: 12px;
            background-color: #fff2f2;
            padding: 8px;
            border: 1px solid #ffcccc;
        """)

        layout.addWidget(warning)


# ======================= PAGE 1 : Données de l'entreprise =======================
class InputPage1(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # ---------- Budget ----------
        self.budget = QDoubleSpinBox()
        self.budget.setMaximum(1e9)
        self.budget.setDecimals(0)
        self.budget.setSuffix(" TND")

        # ---------- Nombre employés ----------
        self.employees = QSpinBox()
        self.employees.setMaximum(100000)

        # ---------- Machines ----------
        self.machineTable = QTableWidget(0, 2)
        self.machineTable.setHorizontalHeaderLabels(["Type Machine", "Quantité"])

        # Boutons ajout/suppression machines
        btn_layout = QHBoxLayout()
        self.add_machine_btn = QPushButton("➕ Ajouter machine")
        self.del_machine_btn = QPushButton("➖ Supprimer machine sélectionnée")
        btn_layout.addWidget(self.add_machine_btn)
        btn_layout.addWidget(self.del_machine_btn)

        # ---------- Bouton Next ----------
        self.nextBtn = QPushButton("➡ Suivant")

        # ---------- Placement ----------
        layout.addWidget(QLabel("💰 Budget disponible"))
        layout.addWidget(self.budget)

        layout.addWidget(QLabel("🧑‍🔧 Nombre d'employés"))
        layout.addWidget(self.employees)

        layout.addWidget(QLabel("⚙️ Machines disponibles"))
        layout.addWidget(self.machineTable)
        layout.addLayout(btn_layout)

        layout.addWidget(self.nextBtn)
        self.setLayout(layout)

        # Connexions
        self.add_machine_btn.clicked.connect(self.add_machine_row)
        self.del_machine_btn.clicked.connect(self.remove_machine_row)
        self.backBtn = QPushButton("🏠 Retour à l'accueil")
        layout.addWidget(self.backBtn)

    def add_machine_row(self):
        row = self.machineTable.rowCount()
        self.machineTable.insertRow(row)
        # Valeurs par défaut
        self.machineTable.setItem(row, 0, QTableWidgetItem(f"Machine {row+1}"))
        self.machineTable.setItem(row, 1, QTableWidgetItem("0"))

    def remove_machine_row(self):
        row = self.machineTable.currentRow()
        if row >= 0:
            self.machineTable.removeRow(row)


class InputPage2(QWidget):
    def __init__(self,mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        self.cash_data = {}
        self.current_project = None

        main_layout = QVBoxLayout()

        # ==================== TABLEAU PROJETS ====================
        self.projectTable = QTableWidget(0, 10)  # <-- 10 colonnes maintenant
        self.projectTable.setHorizontalHeaderLabels([
            "Nom projet",
            "Taux sans risque (%)",
            "Prime de risque (%)",
            "Taux actualisation (%)",
            "Durée",
            "Unité",
            "Invest. initial (TND)",
            "VAN (TND)",
            "Employés requis",  # <-- NEW
            "Machines requises"  # <-- NEW
        ])

        self.projectTable.itemSelectionChanged.connect(self.on_project_selection_changed)

        # ==================== BOUTONS PROJET ====================
        proj_btn_layout = QHBoxLayout()
        self.add_proj_btn = QPushButton("➕ Projet")
        self.del_proj_btn = QPushButton("➖ Supprimer")
        self.calc_rate_btn = QPushButton("⚙ Taux")
        self.calc_npv_btn = QPushButton("📌 VAN")

        proj_btn_layout.addWidget(self.add_proj_btn)
        proj_btn_layout.addWidget(self.del_proj_btn)
        proj_btn_layout.addWidget(self.calc_rate_btn)
        proj_btn_layout.addWidget(self.calc_npv_btn)

        # ==================== TABLEAU CASH-FLOW ====================
        self.cashTable = QTableWidget(0, 2)
        self.cashTable.setHorizontalHeaderLabels(["Période", "Cash Flow (TND)"])

        cf_btn_layout = QHBoxLayout()
        self.add_cf_btn = QPushButton("➕ Période")
        self.del_cf_btn = QPushButton("➖ Supprimer")
        cf_btn_layout.addWidget(self.add_cf_btn)
        cf_btn_layout.addWidget(self.del_cf_btn)


        self.solveBtn = QPushButton("🚀 Optimiser la sélection des projets")


        self.solveBtn.clicked.connect(self.run_optimization)

        # Placement UI
        main_layout.addWidget(QLabel("📊 Liste des projets"))
        main_layout.addWidget(self.projectTable)
        main_layout.addLayout(proj_btn_layout)

        main_layout.addWidget(QLabel("💶 Cash-flow du projet sélectionné"))
        main_layout.addWidget(self.cashTable)
        main_layout.addLayout(cf_btn_layout)
        main_layout.addWidget(self.solveBtn)
        self.backBtn = QPushButton("🏠 Retour à l'accueil")


        def show_van_chart(self):
            names = []
            vans = []

            for r in range(self.projectTable.rowCount()):
                van_item = self.projectTable.item(r, 7)
                if van_item and van_item.text() != "":
                    names.append(self.projectTable.item(r, 0).text())
                    vans.append(float(van_item.text()))

            if not vans:
                QMessageBox.warning(self, "Erreur", "Aucune VAN calculée")
                return

            self.canvas = MplCanvas()
            self.canvas.ax.bar(names, vans)
            self.canvas.ax.set_title("Comparaison des VAN des projets")
            self.canvas.ax.set_ylabel("VAN (TND)")
            self.canvas.ax.set_xticklabels(names, rotation=45, ha="right")

            dlg = QWidget()
            dlg.setWindowTitle("📊 VAN des projets")
            l = QVBoxLayout()
            l.addWidget(self.canvas)
            dlg.setLayout(l)
            dlg.resize(600, 400)
            dlg.show()

        self.cfGraphBtn = QPushButton("📈 Cash-flow du projet")
        main_layout.addWidget(self.cfGraphBtn)
        self.cfGraphBtn.clicked.connect(self.show_cashflow_chart)

        self.graphBtn = QPushButton("📊 Afficher graphique VAN")
        main_layout.addWidget(self.graphBtn)
        self.graphBtn.clicked.connect(self.show_van_chart)
        main_layout.addWidget(self.backBtn)

        self.setLayout(main_layout)
        self.backBtn.clicked.connect(lambda: self.mainWindow.pages.setCurrentIndex(0))

        # ==================== EVENTS ====================
        self.add_proj_btn.clicked.connect(self.add_project_row)
        self.del_proj_btn.clicked.connect(self.remove_project)
        self.calc_rate_btn.clicked.connect(self.compute_rate_for_selected)
        self.calc_npv_btn.clicked.connect(self.compute_npv)

        self.add_cf_btn.clicked.connect(self.add_cf)
        self.del_cf_btn.clicked.connect(self.remove_cf)

    def show_van_chart(self):
        names = []
        vans = []

        for r in range(self.projectTable.rowCount()):
            van_item = self.projectTable.item(r, 7)
            if van_item and van_item.text() != "":
                names.append(self.projectTable.item(r, 0).text())
                vans.append(float(van_item.text()))

        if not vans:
            QMessageBox.warning(self, "Erreur", "Aucune VAN calculée")
            return

        self.canvas = MplCanvas()
        self.canvas.ax.bar(names, vans)
        self.canvas.ax.set_title("Comparaison des VAN des projets")
        self.canvas.ax.set_ylabel("VAN (TND)")
        self.canvas.ax.tick_params(axis='x', rotation=45)

        self.graphWindow = QWidget()
        self.graphWindow.setWindowTitle("📊 VAN des projets")
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.graphWindow.setLayout(layout)
        self.graphWindow.resize(600, 400)
        self.graphWindow.show()

    def show_cashflow_chart(self):
        row = self.projectTable.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erreur", "Sélectionne un projet")
            return

        flows = self.cash_data.get(row, [])
        if not flows:
            QMessageBox.warning(self, "Erreur", "Aucun cash-flow pour ce projet")
            return

        periods = [int(p) for p, _ in flows]
        values = [float(cf) for _, cf in flows]

        self.cfCanvas = MplCanvas()
        self.cfCanvas.ax.plot(periods, values, marker='o')
        self.cfCanvas.ax.set_title("Cash-flow du projet")
        self.cfCanvas.ax.set_xlabel("Période")
        self.cfCanvas.ax.set_ylabel("Cash-flow (TND)")
        self.cfCanvas.ax.grid(True)

        # 🔥 fenêtre persistante
        self.cfGraphWindow = QWidget()
        self.cfGraphWindow.setWindowTitle("📈 Cash-flow du projet")
        layout = QVBoxLayout()
        layout.addWidget(self.cfCanvas)
        self.cfGraphWindow.setLayout(layout)
        self.cfGraphWindow.resize(600, 400)
        self.cfGraphWindow.show()

    # ============================ ADD PROJECT ============================

    def add_project_row(self):
        row = self.projectTable.rowCount()
        self.projectTable.insertRow(row)

        self.projectTable.setItem(row, 0, QTableWidgetItem(f"Projet {row + 1}"))
        self.projectTable.setItem(row, 1, QTableWidgetItem("0.0"))
        self.projectTable.setItem(row, 2, QTableWidgetItem("0.0"))
        self.projectTable.setItem(row, 3, QTableWidgetItem("0.0"))
        self.projectTable.setItem(row, 4, QTableWidgetItem("1"))

        unit_combo = QComboBox()
        unit_combo.addItems(["Années", "Mois", "Trimestres"])
        self.projectTable.setCellWidget(row, 5, unit_combo)

        self.projectTable.setItem(row, 6, QTableWidgetItem("0.0"))
        self.projectTable.setItem(row, 7, QTableWidgetItem(""))

        # NEW employee & machine fields
        self.projectTable.setItem(row, 8, QTableWidgetItem("1"))  # employés par défaut
        self.projectTable.setItem(row, 9, QTableWidgetItem("1"))  # machines par défaut

        self.cash_data[row] = []

    # ============================ REMOVE PROJECT ============================

    def remove_project(self):
        row = self.projectTable.currentRow()
        if row >= 0:
            self.projectTable.removeRow(row)
            self.cash_data.pop(row, None)

    # ============================ CALCUL TAUX ============================

    def compute_rate_for_selected(self):
        row = self.projectTable.currentRow()
        if row < 0: return

        rf = float(self.projectTable.item(row, 1).text())
        rp = float(self.projectTable.item(row, 2).text())
        self.projectTable.setItem(row, 3, QTableWidgetItem(f"{rf + rp:.2f}"))

    # ============================ CASH-FLOW ============================

    def add_cf(self):
        if self.current_project is None: return

        r = self.cashTable.rowCount()
        self.cashTable.insertRow(r)
        self.cashTable.setItem(r, 0, QTableWidgetItem(str(r + 1)))
        self.cashTable.setItem(r, 1, QTableWidgetItem("0.0"))

    def remove_cf(self):
        r = self.cashTable.currentRow()
        if r >= 0: self.cashTable.removeRow(r)

    # ============== SWITCH PROJET (Sauvegarde + Chargement CF) ==============

    def on_project_selection_changed(self):
        row = self.projectTable.currentRow()
        if row < 0: return

        if self.current_project is not None:
            self.save_cashflows(self.current_project)

        self.current_project = row
        self.load_cashflows(row)

    def save_cashflows(self, index):
        data = []
        for r in range(self.cashTable.rowCount()):
            data.append((self.cashTable.item(r, 0).text(), self.cashTable.item(r, 1).text()))
        self.cash_data[index] = data

    def load_cashflows(self, index):
        self.cashTable.setRowCount(0)
        for p, cf in self.cash_data.get(index, []):
            r = self.cashTable.rowCount()
            self.cashTable.insertRow(r)
            self.cashTable.setItem(r, 0, QTableWidgetItem(p))
            self.cashTable.setItem(r, 1, QTableWidgetItem(cf))

    # ============================ CALCUL VAN 🔥 ============================

    def compute_npv(self):
        row = self.projectTable.currentRow()
        if row < 0: return

        r = float(self.projectTable.item(row, 3).text()) / 100
        unit = self.projectTable.cellWidget(row, 5).currentText()

        if unit == "Années":
            period_rate = r
        elif unit == "Mois":
            period_rate = (1 + r) ** (1 / 12) - 1
        else:
            period_rate = (1 + r) ** (1 / 4) - 1

        I0 = float(self.projectTable.item(row, 6).text())

        VAN = 0
        for p, cf in self.cash_data.get(row, []):
            VAN += float(cf) / ((1 + period_rate) ** int(p))
        VAN -= I0

        self.projectTable.setItem(row, 7, QTableWidgetItem(f"{VAN:.2f}"))

    def run_optimization(self):
        from optimizer import optimize_projects

        data = []

        for r in range(self.projectTable.rowCount()):

            # Vérification VAN
            van_cell = self.projectTable.item(r, 7)
            if van_cell is None or van_cell.text() == "":
                continue  # projet ignoré si VAN pas calculée

            try:
                item = {
                    "name": self.projectTable.item(r, 0).text(),
                    "VAN": float(van_cell.text()),
                    "I0": float(self.projectTable.item(r, 6).text()),
                    "emp": float(self.projectTable.item(r, 8).text()),
                    "mach": float(self.projectTable.item(r, 9).text())
                }
            except:
                continue  # si une seule donnée est invalide -> projet ignoré

            data.append(item)

        # Contraintes ressources globales récupérées depuis Page1 🔥
        data.insert(0, {
            "global":{
                "budget": self.mainWindow.page1.budget.value(),
                "employees": self.mainWindow.page1.employees.value(),
                "machines": sum(int(self.mainWindow.page1.machineTable.item(i,1).text())
                                for i in range(self.mainWindow.page1.machineTable.rowCount()))

            }
        })

        selected, total = optimize_projects(data)

        msg = QMessageBox()
        msg.setWindowTitle("Résultat optimisation Gurobi")
        msg.setText(f"🚀 Projets retenus :\n\n"+"\n".join(selected)+f"\n\n💰 VAN totale = {total:.2f} TND")
        msg.exec()

# ======================= FENÊTRE PRINCIPALE =======================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("🔷 Capital Budgeting App - PyQt6")

        self.pages = QStackedWidget()

        self.home = HomePage()
        self.page1 = InputPage1()
        self.page2 = InputPage2(self)

        self.pages.addWidget(self.home)  # index 0
        self.pages.addWidget(self.page1)  # index 1
        self.pages.addWidget(self.page2)  # index 2

        layout = QVBoxLayout()
        layout.addWidget(self.pages)
        self.setLayout(layout)

        # Navigation Home → P1 / Tests
        self.home.btn_data.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        self.home.btn_test1.clicked.connect(self.run_test1)
        self.home.btn_test2.clicked.connect(self.run_test2)

        self.page1.nextBtn.clicked.connect(self.goto_page2)
        self.page1.backBtn.clicked.connect(lambda: self.pages.setCurrentIndex(0))

    def goto_page2(self):
        self.pages.setCurrentIndex(2)


    # ========================= 🔥 TEST 1 =========================
    def run_test1(self):
        self.pages.setCurrentIndex(1)
        self.page1.budget.setValue(120000)
        self.page1.employees.setValue(20)

        self.page1.machineTable.setRowCount(1)
        self.page1.machineTable.setItem(0,0,QTableWidgetItem("Machine A"))
        self.page1.machineTable.setItem(0,1,QTableWidgetItem("10"))

        self.goto_page2()
        self.page2.projectTable.setRowCount(0)
        self.page2.cash_data={}

        sample=[
            ("Projet 1",50000,[30000,35000,40000],3,4,3,"Années",5,3),
            ("Projet 2",40000,[20000,28000,30000],3,3,3,"Années",4,2),
            ("Projet 3",70000,[35000,42000,50000],3,6,3,"Années",7,5)
        ]

        for name,I0,CFs,rf,rp,dur,unit,emp,mach in sample:
            self.page2.add_project_row()
            r=self.page2.projectTable.rowCount()-1
            self.page2.projectTable.setItem(r,0,QTableWidgetItem(name))
            self.page2.projectTable.setItem(r,1,QTableWidgetItem(str(rf)))
            self.page2.projectTable.setItem(r,2,QTableWidgetItem(str(rp)))
            self.page2.projectTable.setItem(r,4,QTableWidgetItem(str(dur)))
            self.page2.projectTable.cellWidget(r,5).setCurrentText(unit)
            self.page2.projectTable.setItem(r,6,QTableWidgetItem(str(I0)))
            self.page2.projectTable.setItem(r,8,QTableWidgetItem(str(emp)))
            self.page2.projectTable.setItem(r,9,QTableWidgetItem(str(mach)))

            self.page2.cash_data[r]=[(str(i+1),str(cf)) for i,cf in enumerate(CFs)]
            self.page2.compute_rate_for_selected()
            self.page2.compute_npv()


    # ========================= 🚀 TEST 2 =========================
    def run_test2(self):
        import random

        self.pages.setCurrentIndex(1)
        self.page1.budget.setValue(600000)
        self.page1.employees.setValue(80)

        self.page1.machineTable.setRowCount(1)
        self.page1.machineTable.setItem(0,0,QTableWidgetItem("Machine X"))
        self.page1.machineTable.setItem(0,1,QTableWidgetItem("45"))

        self.goto_page2()
        self.page2.projectTable.setRowCount(0)
        self.page2.cash_data={}

        for i in range(10):
            self.page2.add_project_row()
            I0=random.randint(20000,90000)
            emp=random.randint(3,10)
            mach=random.randint(1,7)

            rf=3
            rp=random.randint(2,7)
            dur=3
            CFs=[random.randint(15000,60000) for _ in range(dur)]

            r=self.page2.projectTable.rowCount()-1
            self.page2.projectTable.setItem(r,0,QTableWidgetItem(f"Projet Auto {i+1}"))
            self.page2.projectTable.setItem(r,1,QTableWidgetItem(str(rf)))
            self.page2.projectTable.setItem(r,2,QTableWidgetItem(str(rp)))
            self.page2.projectTable.setItem(r,4,QTableWidgetItem(str(dur)))
            self.page2.projectTable.cellWidget(r,5).setCurrentText("Années")
            self.page2.projectTable.setItem(r,6,QTableWidgetItem(str(I0)))
            self.page2.projectTable.setItem(r,8,QTableWidgetItem(str(emp)))
            self.page2.projectTable.setItem(r,9,QTableWidgetItem(str(mach)))

            self.page2.cash_data[r]=[(str(i+1),str(c)) for i,c in enumerate(CFs)]
            self.page2.compute_rate_for_selected()
            self.page2.compute_npv()

        QMessageBox.information(self,"⚡ Test 2 prêt","10 projets auto générés !")



# ======================= RUN APP =======================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

import os
import sys

# Constants and Configuration - 'Gerador de BOT' Premium Theme
COR_PRINCIPAL = "#1F6AA5"   # Blue
COR_HOVER = "#144870"       # Darker Blue
COR_TEXTO_TITULO = "#FFFFFF" # Pure White
COR_FUNDO_APP = "#0F0F0F"    # Darkest Sidebar/Bg
COR_FUNDO_CONTENT = "#1E1E1E" # Lighter Content Frame
COR_FUNDO_LISTA = "#242424"   # Section Bg
COR_PERIGOSA = "#C93B3B"      # Red
COR_AVISO = "#D97706"         # Yellow/Orange (Editar)
COR_SUCESSO = "#1F6AA5"       # Consistent Blue for positive
COR_BORDAS = "#333333"        # Subtle Border

# Access Configuration
# IMPORTANT: Sensitive data removed from hardcoded constants
DEFAULT_CONFIG_FILE = "config.json"

VAR_DESCRIPTIONS = {
    '$SLOT': 'Slot GPON',
    '$PON': 'Porta PON',
    '$ONU_ID': '(Automático)',
    '$SN': '(Automático)',
    '$DESC': 'Descrição/Cliente',
    '$VLAN': 'VLAN Internet',
    '$CVLAN': 'C-VLAN',
    '$SVLAN': 'S-VLAN',
    '$COS': 'CoS/Prioridade',
    '$TEL_VLAN': 'VLAN VoIP',
    '$PORT': 'Porta LAN',
    '$HW_LINE_PRF_NAME': 'Nome do Line Profile (Name)',
    '$HW_SRV_PRF_NAME': 'Nome do Srv Profile (Name)',
    '$HW_LINE_PRF_GEM': 'Gemport ID (Número)',
    '$HW_TRF_PRF_NAME': 'Traffic Table (Name)',
}

PRIORITY_ORDER = [
    '$SLOT', '$PON', '$DESC', '$VLAN', '$CVLAN', '$SVLAN',
    '$TEL_VLAN', '$PORT', '$COS',
    '$HW_LINE_PRF_NAME', '$HW_SRV_PRF_NAME', '$HW_LINE_PRF_GEM', '$HW_TRF_PRF_NAME'
]

AVAILABLE_VARS = list(VAR_DESCRIPTIONS.keys())

# OLT Manufacturers and Models
OLT_MODELS = {
    "Huawei": ["Geral"],
    "ZTE": ["C3xx", "C6xx"],
    "Fiberhome": ["RP700", "RP1000-RP1900", "AN6000"],
    "Datacom": ["Geral"],
    "Nokia": ["Geral"],
    "Parks": ["Geral"],
    "Vsol": ["Geral"],
    "TP-Link": ["Geral"]
}

# Manufacturer-specific variables (to be filtered in the UI)
VARS_HUAWEI = ['$HW_LINE_PRF_NAME', '$HW_SRV_PRF_NAME', '$HW_LINE_PRF_GEM', '$HW_TRF_PRF_NAME']

TEMPLATES_PADRAO = {
    "Huawei": {
        "Geral": {
            "Router Generico": """ont add $PON $ONU_ID sn-auth $SN omci ont-lineprofile-name $HW_LINE_PRF_NAME ont-srvprofile-name $HW_SRV_PRF_NAME desc "$DESC"
ont port native-vlan $PON $ONU_ID eth 1 vlan $VLAN priority 0
ont port route $PON $ONU_ID eth 1-4 enable
quit
service-port vlan $VLAN gpon 0/$SLOT/$PON ont $ONU_ID gemport $HW_LINE_PRF_GEM multi-service user-vlan $VLAN tag-transform translate inbound traffic-table name $HW_TRF_PRF_NAME outbound traffic-table name $HW_TRF_PRF_NAME""",

            "Bridge": """ont add $PON $ONU_ID sn-auth $SN omci ont-lineprofile-name $HW_LINE_PRF_NAME ont-srvprofile-name $HW_SRV_PRF_NAME desc "$DESC"
ont port native-vlan $PON $ONU_ID eth 1 vlan $VLAN priority 0
quit
service-port vlan $VLAN gpon 0/$SLOT/$PON ont $ONU_ID gemport $HW_LINE_PRF_GEM multi-service user-vlan $VLAN tag-transform translate inbound traffic-table name $HW_TRF_PRF_NAME outbound traffic-table name $HW_TRF_PRF_NAME""",

            "Veip": """ont add $PON $ONU_ID sn-auth $SN omci ont-lineprofile-name $HW_LINE_PRF_NAME ont-srvprofile-name $HW_SRV_PRF_NAME desc "$DESC"
ont port vlan $PON $ONU_ID iphost translation $VLAN user-vlan $VLAN
quit
service-port vlan $VLAN gpon 0/$SLOT/$PON ont $ONU_ID gemport $HW_LINE_PRF_GEM multi-service user-vlan $VLAN tag-transform translate inbound traffic-table name $HW_TRF_PRF_NAME outbound traffic-table name $HW_TRF_PRF_NAME"""
        }
    }
}

def get_app_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

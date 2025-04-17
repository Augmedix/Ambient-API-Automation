class Data:
    update_dr_status_query = f"UPDATE `doctor` SET `doctorStatus` = '##doctorStatus##' WHERE (`doctorEmail` = '##doctorEmail##')"
    get_note_query = "query getANote {\n  getNote(noteId: \"##noteID##\") {\n    noteId    \n  }\n}"
    get_note_complaints_selection_query = "query getANotesOrganizeSelections {\n  listComplaintsSelection(noteId: \"##noteID##\") {\n    items {\n      ComplaintId\n      ComplaintName\n      ChiefComplaint\n      ComplaintType\n      Section\n      ActionSource\n      SourceEventName\n      descriptorSelections {\n        items {\n          ElementName\n          ElementId\n          ElementVariationId\n          DescriptorId\n          DescriptorName\n          ComplaintId\n          ElementDataSourceType\n          Data\n          DataType\n          ParentElementId\n          ParentDescriptorId\n          IdentityLabel\n          Value\n          Section\n          ActionSource\n          SourceEventName\n          DescriptorGroupId\n          DescriptorGroupType\n        }\n      }\n      sentences {\n        items {\n          Section\n          ComplaintId\n          ElementId\n          Sentence\n        }\n      }\n    }\n  }\n}"
    get_note_organize_selection_query = 'getNote(noteId: \"##noteID##\") {\n  noteId\n  patientAge: organizeSelections(filter: {IdentityLabel: {eq: "PatientAge"}}) {\n    items {\n      noteId\n      Section\n      selection\n      IdentityLabel\n      Data\n      DataType\n      Unit\n    }\n  }\n  patientGender: organizeSelections(filter: {IdentityLabel: {eq: "PatientGender"}}) {\n    items {\n      noteId\n      Section\n      selection\n      IdentityLabel\n      Data\n      DataType\n    }\n  }\n}'
    doctorIdPlaceholder = '##doctorId##'
    doctorStatusPlaceholder = '##doctorStatus##'
    doctorEmailPlaceholder = '##doctorEmail##'
    noteIDPlaceholder = '##noteID##'
    doctorPasswordHashPlaceholder = '##passwordHash##'

    update_dr_password_query = f"UPDATE `doctor` SET `doctorPassword` = '##passwordHash##' WHERE (`doctorEmail` = '##doctorEmail##');"

    lynx_hpi_chronic_blocks = ['Symptoms', 'Current medications*', 'Lifestyle treatments', 'Recent Labs*']
    lynx_ap_chronic_blocks = ['Status', 'Progression', 'Medications', 'Lifestyle treatments', 'Labs']
    lynx_hpi_acute_blocks = ['Symptoms', 'Current medications*', 'Lifestyle treatments', 'Recent Labs*']
    lynx_ap_acute_blocks = ['Status', 'Progression', 'Medications', 'Lifestyle treatments', 'Labs']


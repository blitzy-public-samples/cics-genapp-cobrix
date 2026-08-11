******************************************************************
*  COPYBOOK  : GODCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : DC
******************************************************************
 01  RT-ODC-RATING.

          03 RT-ODC-TERRITORY-CODE            PIC X(3).
          03 RT-ODC-CLASS-CODE                PIC X(4).
          03 RT-ODC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ODC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ODC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ODC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ODC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ODC-RATED-PREMIUM             PIC 9(9)V9(2).

******************************************************************
*  COPYBOOK  : GPDCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : DC
******************************************************************
 01  RT-PDC-RATING.

          03 RT-PDC-TERRITORY-CODE            PIC X(3).
          03 RT-PDC-CLASS-CODE                PIC X(4).
          03 RT-PDC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PDC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PDC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PDC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PDC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PDC-RATED-PREMIUM             PIC 9(9)V9(2).

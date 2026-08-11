******************************************************************
*  COPYBOOK  : GFDCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : DC
******************************************************************
 01  RT-FDC-RATING.

          03 RT-FDC-TERRITORY-CODE            PIC X(3).
          03 RT-FDC-CLASS-CODE                PIC X(4).
          03 RT-FDC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FDC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FDC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FDC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FDC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FDC-RATED-PREMIUM             PIC 9(9)V9(2).

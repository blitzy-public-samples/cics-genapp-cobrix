******************************************************************
*  COPYBOOK  : GONVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : NV
******************************************************************
 01  RT-ONV-RATING.

          03 RT-ONV-TERRITORY-CODE            PIC X(3).
          03 RT-ONV-CLASS-CODE                PIC X(4).
          03 RT-ONV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ONV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ONV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ONV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ONV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ONV-RATED-PREMIUM             PIC 9(9)V9(2).

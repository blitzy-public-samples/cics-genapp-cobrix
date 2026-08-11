******************************************************************
*  COPYBOOK  : GMNVR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : NV
******************************************************************
 01  RT-MNV-RATING.

          03 RT-MNV-TERRITORY-CODE            PIC X(3).
          03 RT-MNV-CLASS-CODE                PIC X(4).
          03 RT-MNV-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MNV-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MNV-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MNV-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MNV-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MNV-RATED-PREMIUM             PIC 9(9)V9(2).

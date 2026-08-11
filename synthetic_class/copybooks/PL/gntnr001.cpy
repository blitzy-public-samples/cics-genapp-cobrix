******************************************************************
*  COPYBOOK  : GNTNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : TN
******************************************************************
 01  RT-NTN-RATING.

          03 RT-NTN-TERRITORY-CODE            PIC X(3).
          03 RT-NTN-CLASS-CODE                PIC X(4).
          03 RT-NTN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NTN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NTN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NTN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NTN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NTN-RATED-PREMIUM             PIC 9(9)V9(2).

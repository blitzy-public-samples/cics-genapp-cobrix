******************************************************************
*  COPYBOOK  : GFSDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : SD
******************************************************************
 01  RT-FSD-RATING.

          03 RT-FSD-TERRITORY-CODE            PIC X(3).
          03 RT-FSD-CLASS-CODE                PIC X(4).
          03 RT-FSD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FSD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FSD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FSD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FSD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FSD-RATED-PREMIUM             PIC 9(9)V9(2).

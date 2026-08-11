******************************************************************
*  COPYBOOK  : GFVTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : VT
******************************************************************
 01  RT-FVT-RATING.

          03 RT-FVT-TERRITORY-CODE            PIC X(3).
          03 RT-FVT-CLASS-CODE                PIC X(4).
          03 RT-FVT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FVT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FVT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FVT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FVT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FVT-RATED-PREMIUM             PIC 9(9)V9(2).

******************************************************************
*  COPYBOOK  : GFNER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : NE
******************************************************************
 01  RT-FNE-RATING.

          03 RT-FNE-TERRITORY-CODE            PIC X(3).
          03 RT-FNE-CLASS-CODE                PIC X(4).
          03 RT-FNE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FNE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FNE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FNE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FNE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FNE-RATED-PREMIUM             PIC 9(9)V9(2).
